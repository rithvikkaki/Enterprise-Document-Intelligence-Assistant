import uuid
from typing import Optional, Any, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, Enum, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin
from app.models.document_version import ProcessingStatusEnum

if TYPE_CHECKING:
    from app.models.document_version import DocumentVersion

JSON_TYPE = JSON().with_variant(JSONB, "postgresql")


class ProcessingJob(Base, TimestampMixin):
    __tablename__ = "processing_jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    document_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("document_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    status: Mapped[ProcessingStatusEnum] = mapped_column(
        Enum(ProcessingStatusEnum), default=ProcessingStatusEnum.QUEUED, nullable=False
    )
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    metadata_json: Mapped[Optional[Any]] = mapped_column(JSON_TYPE, nullable=True, default=dict)

    document_version: Mapped["DocumentVersion"] = relationship("DocumentVersion", back_populates="processing_jobs")
