import uuid
from typing import Optional, Any, TYPE_CHECKING
from sqlalchemy import String, Text, Integer, ForeignKey, Index, JSON
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from app.db.base import Base, TimestampMixin
from app.core.config import settings

if TYPE_CHECKING:
    from app.models.document_version import DocumentVersion

# Use PostgreSQL JSONB / TSVECTOR / Vector with cross-database fallback for SQLite test runner
JSON_TYPE = JSON().with_variant(JSONB, "postgresql")
TSVECTOR_TYPE = Text().with_variant(TSVECTOR, "postgresql")


class DocumentChunk(Base, TimestampMixin):
    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    document_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("document_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False)
    metadata_json: Mapped[Optional[Any]] = mapped_column(JSON_TYPE, nullable=True, default=dict)
    
    # PostgreSQL Full-Text Search TSVector column
    fts_vector: Mapped[Optional[Any]] = mapped_column(TSVECTOR_TYPE, nullable=True)

    # pgvector embedding column (384-dimensional for sentence-transformers/all-MiniLM-L6-v2)
    embedding: Mapped[Optional[Any]] = mapped_column(Vector(settings.EMBEDDING_DIMENSION), nullable=True)

    document_version: Mapped["DocumentVersion"] = relationship("DocumentVersion", back_populates="chunks")

    __table_args__ = (
        Index("ix_chunks_fts_vector", "fts_vector", postgresql_using="gin"),
        Index(
            "ix_chunks_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

