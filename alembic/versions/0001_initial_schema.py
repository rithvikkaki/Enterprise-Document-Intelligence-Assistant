"""initial_schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-09-11 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import pgvector

revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ensure pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )

    # organizations table
    op.create_table(
        'organizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )

    # memberships table
    op.create_table(
        'memberships',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('role', sa.Enum('OWNER', 'ADMIN', 'EDITOR', 'VIEWER', name='roleenum'), nullable=False, server_default='VIEWER'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.UniqueConstraint('organization_id', 'user_id', name='uq_organization_user'),
    )

    # projects table
    op.create_table(
        'projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.UniqueConstraint('organization_id', 'name', name='uq_org_project_name'),
    )

    # documents table
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('mime_type', sa.String(128), nullable=False),
        sa.Column('current_version_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )

    # document_versions table
    op.create_table(
        'document_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('version_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('original_filename', sa.String(255), nullable=False),
        sa.Column('storage_path', sa.String(512), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=False),
        sa.Column('mime_type', sa.String(128), nullable=False),
        sa.Column('checksum', sa.String(64), nullable=False),
        sa.Column('idempotency_key', sa.String(255), nullable=True, index=True),
        sa.Column('uploaded_by_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('processing_status', sa.Enum('UPLOADED', 'QUEUED', 'PROCESSING', 'EXTRACTING', 'OCR_PROCESSING', 'NORMALIZING', 'LANGUAGE_DETECTION', 'CHUNKING', 'EMBEDDING', 'INDEXING', 'COMPLETED', 'FAILED', name='processingstatusenum'), nullable=False, server_default='UPLOADED'),
        sa.Column('detected_language', sa.String(10), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.UniqueConstraint('document_id', 'version_number', name='uq_document_version_number'),
    )

    # FK from documents.current_version_id to document_versions.id
    op.create_foreign_key(
        'fk_documents_current_version_id',
        'documents', 'document_versions',
        ['current_version_id'], ['id'],
        ondelete='SET NULL', use_alter=True
    )

    # document_chunks table
    op.create_table(
        'document_chunks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('document_version_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('document_versions.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('token_count', sa.Integer(), nullable=False),
        sa.Column('metadata_json', postgresql.JSONB(), nullable=True),
        sa.Column('fts_vector', postgresql.TSVECTOR(), nullable=True),
        sa.Column('embedding', pgvector.sqlalchemy.Vector(384), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )
    op.create_index('ix_chunks_fts_vector', 'document_chunks', ['fts_vector'], postgresql_using='gin')
    op.execute("CREATE INDEX IF NOT EXISTS ix_chunks_embedding_hnsw ON document_chunks USING hnsw (embedding vector_cosine_ops);")



    # processing_jobs table
    op.create_table(
        'processing_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('document_version_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('document_versions.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('status', sa.Enum('UPLOADED', 'QUEUED', 'PROCESSING', 'EXTRACTING', 'OCR_PROCESSING', 'NORMALIZING', 'LANGUAGE_DETECTION', 'CHUNKING', 'EMBEDDING', 'INDEXING', 'COMPLETED', 'FAILED', name='processingstatusenum'), nullable=False, server_default='QUEUED'),
        sa.Column('progress_percentage', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_code', sa.String(64), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata_json', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )

    # api_keys table
    op.create_table(
        'api_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('key_prefix', sa.String(32), nullable=False, index=True),
        sa.Column('hashed_key', sa.String(255), nullable=False),
        sa.Column('scopes', postgresql.JSONB(), nullable=True),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )

    # audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('action', sa.String(64), nullable=False, index=True),
        sa.Column('resource_type', sa.String(64), nullable=False),
        sa.Column('resource_id', sa.String(255), nullable=True),
        sa.Column('request_id', sa.String(64), nullable=True),
        sa.Column('ip_address', sa.String(64), nullable=True),
        sa.Column('metadata_json', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('api_keys')
    op.drop_table('processing_jobs')
    op.execute("DROP INDEX IF EXISTS ix_chunks_embedding_hnsw;")
    op.drop_index('ix_chunks_fts_vector', table_name='document_chunks')
    op.drop_table('document_chunks')
    op.drop_constraint('fk_documents_current_version_id', 'documents', type_='foreignkey')
    op.drop_table('document_versions')
    op.drop_table('documents')
    op.drop_table('projects')
    op.drop_table('memberships')
    op.drop_table('organizations')
    op.drop_table('users')
    op.execute("DROP TYPE IF EXISTS processingstatusenum;")
    op.execute("DROP TYPE IF EXISTS roleenum;")
