import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, File, UploadFile, Header, Form, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.dependencies import get_current_user, require_org_role
from app.models.user import User
from app.models.membership import RoleEnum
from app.schemas.document import DocumentResponse, DocumentVersionResponse, ProcessingJobStatusResponse
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    organization_id: uuid.UUID = Query(...),
    project_id: Optional[uuid.UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service_dep = require_org_role([RoleEnum.VIEWER, RoleEnum.EDITOR, RoleEnum.ADMIN, RoleEnum.OWNER])
    await service_dep(organization_id, current_user, db)
    doc_service = DocumentService(db)
    docs = await doc_service.doc_repo.list_by_org(organization_id, project_id)
    return [DocumentResponse.model_validate(d) for d in docs]


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    organization_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service_dep = require_org_role([RoleEnum.VIEWER, RoleEnum.EDITOR, RoleEnum.ADMIN, RoleEnum.OWNER])
    await service_dep(organization_id, current_user, db)
    doc_service = DocumentService(db)
    doc = await doc_service.doc_repo.get_by_id(document_id, organization_id)
    if not doc:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Document", str(document_id))
    return DocumentResponse.model_validate(doc)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    organization_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Only EDITOR, ADMIN, OWNER can delete; VIEWER is rejected
    service_dep = require_org_role([RoleEnum.EDITOR, RoleEnum.ADMIN, RoleEnum.OWNER])
    await service_dep(organization_id, current_user, db)
    doc_service = DocumentService(db)
    deleted = await doc_service.doc_repo.delete_document(document_id, organization_id)
    if not deleted:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Document", str(document_id))
    return None





@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    organization_id: uuid.UUID = Form(...),
    project_id: uuid.UUID = Form(...),
    document_id: Optional[uuid.UUID] = Form(None),
    file: UploadFile = File(...),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service_dep = require_org_role([RoleEnum.EDITOR, RoleEnum.ADMIN, RoleEnum.OWNER])
    await service_dep(organization_id, current_user, db)

    doc_service = DocumentService(db)
    content = await file.read()

    doc_version, job = await doc_service.upload_document(
        org_id=organization_id,
        project_id=project_id,
        user_id=current_user.id,
        filename=file.filename or "document.txt",
        content=content,
        mime_type=file.content_type or "application/octet-stream",
        existing_document_id=document_id,
        idempotency_key=idempotency_key,
    )

    # Trigger async Celery processing task (bypassed instantly during unit tests)
    if os.environ.get("TESTING") != "true":
        try:
            from app.workers.tasks import process_document_version
            process_document_version.delay(str(doc_version.id))
        except Exception:
            pass

    return {
        "message": "Document uploaded successfully and queued for processing",
        "document_id": str(doc_version.document_id),
        "version_id": str(doc_version.id),
        "job_id": str(job.id),
        "status": job.status,
    }


@router.get("/{document_id}/status", response_model=ProcessingJobStatusResponse)
async def get_document_status(
    document_id: uuid.UUID,
    organization_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service_dep = require_org_role([RoleEnum.VIEWER, RoleEnum.EDITOR, RoleEnum.ADMIN, RoleEnum.OWNER])
    await service_dep(organization_id, current_user, db)

    doc_service = DocumentService(db)
    return await doc_service.get_document_status(document_id, organization_id)


@router.post("/{document_id}/retry", status_code=status.HTTP_202_ACCEPTED)
async def retry_document_processing(
    document_id: uuid.UUID,
    organization_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service_dep = require_org_role([RoleEnum.EDITOR, RoleEnum.ADMIN, RoleEnum.OWNER])
    await service_dep(organization_id, current_user, db)

    doc_service = DocumentService(db)
    doc = await doc_service.doc_repo.get_by_id(document_id, organization_id)
    if not doc or not doc.current_version_id:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Document", str(document_id))

    if os.environ.get("TESTING") != "true":
        from app.workers.tasks import process_document_version
        process_document_version.delay(str(doc.current_version_id))

    return {
        "message": "Document re-processing task queued",
        "document_id": str(document_id),
        "version_id": str(doc.current_version_id),
    }
