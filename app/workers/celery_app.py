from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "enterprise_document_intelligence",
    broker=settings.get_celery_broker(),
    backend=settings.get_celery_backend(),
    include=["app.workers.tasks"],
)

app = celery_app


celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,  # 30 minutes max per task
    task_soft_time_limit=1500,
)
