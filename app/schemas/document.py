import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.models.document_version import ProcessingStatusEnum


class DocumentVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_id: uuid.UUID
    version_number: int
    original_filename: str
    file_size: int
    mime_type: str
    checksum: str
    processing_status: ProcessingStatusEnum
    detected_language: Optional[str] = None
    created_at: datetime


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    project_id: uuid.UUID
    title: str
    mime_type: str
    current_version_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime


class ProcessingJobStatusResponse(BaseModel):
    job_id: uuid.UUID
    document_version_id: uuid.UUID
    status: ProcessingStatusEnum
    progress_percentage: int
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
