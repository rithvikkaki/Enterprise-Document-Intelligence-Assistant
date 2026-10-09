import uuid
import hashlib
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.exceptions import FileValidationError, NotFoundError, PermissionDeniedError
from app.models.document import Document
from app.models.document_version import DocumentVersion, ProcessingStatusEnum
from app.models.processing_job import ProcessingJob
from app.repositories.document_repository import DocumentRepository
from app.repositories.project_repository import ProjectRepository
from app.providers.storage.local_storage import LocalStorageProvider
from app.schemas.document import DocumentResponse, DocumentVersionResponse, ProcessingJobStatusResponse

ALLOWED_EXTENSIONS = {
    "pdf", "docx", "pptx", "xlsx", "html", "htm", "eml", "txt", "md", "markdown",
    "png", "jpg", "jpeg", "zip"
}


class DocumentService:
    def __init__(self, session: AsyncSession):
        self.doc_repo = DocumentRepository(session)
        self.project_repo = ProjectRepository(session)
        self.storage = LocalStorageProvider()

    def validate_file(self, filename: str, content_length: int):
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if content_length > max_bytes:
            raise FileValidationError(
                f"File size exceeds maximum allowed limit of {settings.MAX_UPLOAD_SIZE_MB}MB"
            )

        ext = filename.split(".")[-1].lower() if "." in filename else ""
        if ext not in ALLOWED_EXTENSIONS:
            raise FileValidationError(
                f"Unsupported file type '.{ext}'. Allowed extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )

    async def upload_document(
        self,
        org_id: uuid.UUID,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        filename: str,
        content: bytes,
        mime_type: str,
        existing_document_id: Optional[uuid.UUID] = None,
        idempotency_key: Optional[str] = None,
    ) -> Tuple[DocumentVersion, ProcessingJob]:
        # Ensure project exists & belongs to org
        project = await self.project_repo.get_by_id(project_id, org_id)
        if not project:
            raise NotFoundError("Project", str(project_id))

        self.validate_file(filename, len(content))

        # Check Idempotency-Key
        if idempotency_key:
            existing_ver = await self.doc_repo.get_version_by_idempotency_key(org_id, idempotency_key)
            if existing_ver:
                job = await self.doc_repo.get_latest_job_for_version(existing_ver.id)
                return existing_ver, job

        checksum = hashlib.sha256(content).hexdigest()

        # 1. Fetch or Create Document
        if existing_document_id:
            document = await self.doc_repo.get_by_id(existing_document_id, org_id)
            if not document:
                raise NotFoundError("Document", str(existing_document_id))
        else:
            document = Document(
                organization_id=org_id,
                project_id=project_id,
                title=filename,
                mime_type=mime_type or "application/octet-stream",
            )
            document = await self.doc_repo.create_document(document)

        # 2. Determine Version Number
        current_max_v = await self.doc_repo.get_latest_version_number(document.id)
        version_number = current_max_v + 1

        # 3. Store File using Storage Provider
        version_id = uuid.uuid4()
        relative_path = (
            f"orgs/{org_id.hex[:12]}/proj/{project_id.hex[:12]}/doc/{document.id.hex[:12]}/v_{version_id.hex[:12]}/{filename}"
        )
        storage_path = await self.storage.save_file(relative_path, content)


        # 4. Create DocumentVersion record
        doc_version = DocumentVersion(
            id=version_id,
            document_id=document.id,
            version_number=version_number,
            original_filename=filename,
            storage_path=storage_path,
            file_size=len(content),
            mime_type=mime_type or "application/octet-stream",
            checksum=checksum,
            idempotency_key=idempotency_key,
            uploaded_by_id=user_id,
            processing_status=ProcessingStatusEnum.QUEUED,
        )

        doc_version = await self.doc_repo.create_version(doc_version)

        # Update Document current_version_id
        document.current_version_id = doc_version.id

        # 5. Create ProcessingJob
        job = ProcessingJob(
            document_version_id=doc_version.id,
            organization_id=org_id,
            status=ProcessingStatusEnum.QUEUED,
            progress_percentage=0,
        )
        job = await self.doc_repo.create_processing_job(job)

        # Flush DB changes before returning
        await self.doc_repo.session.flush()
        return doc_version, job

    async def get_document_status(self, document_id: uuid.UUID, org_id: uuid.UUID) -> ProcessingJobStatusResponse:
        document = await self.doc_repo.get_by_id(document_id, org_id)
        if not document or not document.current_version_id:
            raise NotFoundError("Document", str(document_id))

        job = await self.doc_repo.get_latest_job_for_version(document.current_version_id)
        if not job:
            raise NotFoundError("Processing job for document", str(document_id))

        return ProcessingJobStatusResponse(
            job_id=job.id,
            document_version_id=job.document_version_id,
            status=job.status,
            progress_percentage=job.progress_percentage,
            error_code=job.error_code,
            error_message=job.error_message,
            retry_count=job.retry_count,
            started_at=job.started_at,
            completed_at=job.completed_at,
            failed_at=job.failed_at,
        )
