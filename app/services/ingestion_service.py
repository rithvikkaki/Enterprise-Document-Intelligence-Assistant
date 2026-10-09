import uuid
from typing import List
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import logger
from app.models.document_version import DocumentVersion, ProcessingStatusEnum
from app.models.document_chunk import DocumentChunk
from app.models.processing_job import ProcessingJob
from app.providers.storage.local_storage import LocalStorageProvider
from app.services.extraction_service import ExtractionService
from app.services.chunking_service import SentenceBoundaryChunker, FixedSizeChunker, MarkdownChunker
from app.services.embedding_service import EmbeddingService
from app.processing.extractors.zip_handler import SafeZipHandler


class IngestionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.storage = LocalStorageProvider()
        self.extraction_service = ExtractionService()
        self.chunker = SentenceBoundaryChunker()
        self.embedding_service = EmbeddingService()
        self.zip_handler = SafeZipHandler()

    async def process_version(self, version_id: uuid.UUID) -> bool:
        # Fetch DocumentVersion
        stmt = select(DocumentVersion).where(DocumentVersion.id == version_id)
        res = await self.session.execute(stmt)
        doc_version = res.scalar_one_or_none()
        if not doc_version:
            logger.error(f"Ingestion failed: DocumentVersion '{version_id}' not found")
            return False

        # Fetch Document for organization_id and project_id
        from app.models.document import Document
        doc_res = await self.session.execute(select(Document).where(Document.id == doc_version.document_id))
        document = doc_res.scalar_one_or_none()
        if not document:
            logger.error(f"Ingestion failed: Document for version '{version_id}' not found")
            return False

        # Fetch ProcessingJob
        job_stmt = select(ProcessingJob).where(ProcessingJob.document_version_id == version_id)
        job_res = await self.session.execute(job_stmt)
        job = job_res.scalars().first()

        async def update_state(status: ProcessingStatusEnum, progress: int, err_msg: str = None):
            doc_version.processing_status = status
            if job:
                job.status = status
                job.progress_percentage = progress
                if err_msg:
                    job.error_message = err_msg
            await self.session.flush()

        try:
            # 1. State: PROCESSING / EXTRACTING
            await update_state(ProcessingStatusEnum.PROCESSING, 10)
            await update_state(ProcessingStatusEnum.EXTRACTING, 25)

            file_bytes = await self.storage.read_file(doc_version.storage_path)

            ext = doc_version.original_filename.split(".")[-1].lower() if "." in doc_version.original_filename else ""

            extracted_items: List[tuple[str, bytes]] = []
            if ext == "zip":
                extracted_items = self.zip_handler.extract_files(file_bytes)
            else:
                extracted_items = [(doc_version.original_filename, file_bytes)]

            all_chunks_data = []

            for filename, data in extracted_items:
                # 2. Extract text & OCR fallback
                extraction_result = self.extraction_service.process_file(data, filename)
                doc_version.detected_language = extraction_result.metadata.get("detected_language", "en")

                # 3. State: CHUNKING
                await update_state(ProcessingStatusEnum.CHUNKING, 50)
                file_ext = filename.split(".")[-1].lower() if "." in filename else ""
                chunker = MarkdownChunker() if file_ext in ("md", "markdown") else self.chunker
                
                initial_meta = {
                    "filename": filename,
                    "extraction_method": extraction_result.extraction_method,
                    "used_ocr": extraction_result.used_ocr,
                    "detected_language": doc_version.detected_language,
                }
                chunks = chunker.create_chunks(extraction_result.text, initial_meta)
                all_chunks_data.extend(chunks)

            if not all_chunks_data:
                logger.warning(f"No text extracted for document version {version_id}")
                await update_state(ProcessingStatusEnum.COMPLETED, 100)
                return True

            # 4. State: EMBEDDING
            await update_state(ProcessingStatusEnum.EMBEDDING, 75)
            chunk_texts = [c.content for c in all_chunks_data]
            embeddings = self.embedding_service.generate_batch_embeddings(chunk_texts)

            # 5. State: INDEXING (Idempotent cleanup of old chunks before insertion)
            await update_state(ProcessingStatusEnum.INDEXING, 90)
            await self.session.execute(
                delete(DocumentChunk).where(DocumentChunk.document_version_id == version_id)
            )

            # Insert chunks into DocumentChunk table
            def _check_postgres():
                try:
                    bind = getattr(self.session, "bind", None)
                    if bind is not None and hasattr(bind, "dialect"):
                        return bind.dialect.name == "postgresql"
                    bind = self.session.get_bind()
                    if bind is not None and hasattr(bind, "dialect"):
                        return bind.dialect.name == "postgresql"
                except Exception:
                    pass
                from app.core.config import settings
                return "postgresql" in settings.DATABASE_URL

            is_postgres = _check_postgres()
            for idx, c_data in enumerate(all_chunks_data):
                vec = embeddings[idx] if idx < len(embeddings) else None
                fts_val = func.to_tsvector("english", c_data.content) if is_postgres else c_data.content
                chunk_record = DocumentChunk(
                    organization_id=document.organization_id,
                    project_id=document.project_id,
                    document_id=document.id,
                    document_version_id=doc_version.id,
                    chunk_index=c_data.chunk_index,
                    content=c_data.content,
                    token_count=c_data.token_count,
                    metadata_json=c_data.metadata,
                    embedding=vec,
                    fts_vector=fts_val,
                )
                self.session.add(chunk_record)

            await update_state(ProcessingStatusEnum.COMPLETED, 100)
            await self.session.commit()
            logger.info(f"Successfully processed document version {version_id} with {len(all_chunks_data)} chunks.")
            return True

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error processing document version {version_id}: {str(e)}", exc_info=True)
            try:
                ver_res = await self.session.execute(select(DocumentVersion).where(DocumentVersion.id == version_id))
                ver = ver_res.scalar_one_or_none()
                if ver:
                    ver.processing_status = ProcessingStatusEnum.FAILED
                job_res = await self.session.execute(select(ProcessingJob).where(ProcessingJob.document_version_id == version_id))
                failed_job = job_res.scalars().first()
                if failed_job:
                    failed_job.status = ProcessingStatusEnum.FAILED
                    failed_job.progress_percentage = 0
                    failed_job.error_message = str(e)
                await self.session.commit()
            except Exception as persist_err:
                logger.error(f"Failed to persist failure state for version {version_id}: {persist_err}")
            return False

