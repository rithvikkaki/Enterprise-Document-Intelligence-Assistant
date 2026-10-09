import uuid
from typing import Optional, List, Tuple
from sqlalchemy import select, update, func
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import Document
from app.models.document_version import DocumentVersion, ProcessingStatusEnum
from app.models.processing_job import ProcessingJob


class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_document(self, document: Document) -> Document:
        self.session.add(document)
        await self.session.flush()
        return document

    async def create_version(self, version: DocumentVersion) -> DocumentVersion:
        self.session.add(version)
        await self.session.flush()
        return version

    async def create_processing_job(self, job: ProcessingJob) -> ProcessingJob:
        self.session.add(job)
        await self.session.flush()
        return job

    async def get_by_id(self, document_id: uuid.UUID, org_id: uuid.UUID) -> Optional[Document]:
        stmt = select(Document).where(
            Document.id == document_id,
            Document.organization_id == org_id,
            Document.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_document(self, document_id: uuid.UUID, org_id: uuid.UUID) -> bool:
        from datetime import datetime, timezone
        doc = await self.get_by_id(document_id, org_id)
        if not doc:
            return False
        doc.deleted_at = datetime.now(timezone.utc)
        await self.session.flush()
        return True


    async def list_by_project(self, org_id: uuid.UUID, project_id: uuid.UUID) -> List[Document]:
        stmt = select(Document).where(
            Document.organization_id == org_id,
            Document.project_id == project_id,
            Document.deleted_at.is_(None),
        ).order_by(Document.created_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_by_org(self, org_id: uuid.UUID, project_id: Optional[uuid.UUID] = None) -> List[Document]:
        conditions = [Document.organization_id == org_id, Document.deleted_at.is_(None)]
        if project_id:
            conditions.append(Document.project_id == project_id)
        stmt = select(Document).where(*conditions).order_by(Document.created_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_latest_version_number(self, document_id: uuid.UUID) -> int:
        stmt = select(func.max(DocumentVersion.version_number)).where(DocumentVersion.document_id == document_id)
        result = await self.session.execute(stmt)
        max_v = result.scalar()
        return max_v or 0

    async def get_version_by_idempotency_key(self, org_id: uuid.UUID, idempotency_key: str) -> Optional[DocumentVersion]:
        stmt = (
            select(DocumentVersion)
            .join(Document, DocumentVersion.document_id == Document.id)
            .where(
                Document.organization_id == org_id,
                DocumentVersion.idempotency_key == idempotency_key,
                Document.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def get_version(self, version_id: uuid.UUID) -> Optional[DocumentVersion]:
        stmt = select(DocumentVersion).where(DocumentVersion.id == version_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_latest_job_for_version(self, version_id: uuid.UUID) -> Optional[ProcessingJob]:
        stmt = (
            select(ProcessingJob)
            .where(ProcessingJob.document_version_id == version_id)
            .order_by(ProcessingJob.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def update_job_status(
        self,
        job_id: uuid.UUID,
        status: ProcessingStatusEnum,
        progress: int,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
    ):
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        stmt = select(ProcessingJob).where(ProcessingJob.id == job_id)
        res = await self.session.execute(stmt)
        job = res.scalar_one_or_none()
        if job:
            job.status = status
            job.progress_percentage = progress
            if error_code:
                job.error_code = error_code
            if error_message:
                job.error_message = error_message
            if status == ProcessingStatusEnum.PROCESSING and not job.started_at:
                job.started_at = now
            elif status == ProcessingStatusEnum.COMPLETED:
                job.completed_at = now
            elif status == ProcessingStatusEnum.FAILED:
                job.failed_at = now
            await self.session.flush()
