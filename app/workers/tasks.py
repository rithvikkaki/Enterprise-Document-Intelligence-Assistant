import asyncio
import uuid
from app.workers.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.services.ingestion_service import IngestionService
from app.core.logging import logger


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_document_version(self, version_id_str: str):
    logger.info(f"Celery task process_document_version started for version '{version_id_str}'")

    async def _run():
        async with AsyncSessionLocal() as session:
            service = IngestionService(session)
            return await service.process_version(uuid.UUID(version_id_str))

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        success = loop.run_until_complete(_run())
        if not success:
            logger.warning(f"Celery task process_document_version failed for '{version_id_str}', retrying...")
            raise self.retry(exc=RuntimeError("Document processing step returned False"))
    except Exception as exc:
        logger.error(f"Celery task exception: {str(exc)}")
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        raise exc
