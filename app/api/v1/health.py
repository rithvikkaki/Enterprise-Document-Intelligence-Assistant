from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis
from app.db.session import get_db
from app.core.config import settings
from app.core.logging import logger

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}


@router.get("/live")
async def liveness_check():
    return {"status": "alive"}


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    health_status = {"database": "unknown", "redis": "unknown"}
    is_ready = True

    # 1. Verify PostgreSQL Database
    try:
        await db.execute(text("SELECT 1"))
        health_status["database"] = "healthy"
    except Exception as e:
        logger.error(f"Readiness check database failure: {str(e)}")
        health_status["database"] = f"unhealthy: {str(e)}"
        is_ready = False

    # 2. Verify Redis Connection
    try:
        r = aioredis.from_url(settings.REDIS_URL, socket_timeout=2.0)
        pong = await r.ping()
        await r.aclose()
        if pong:
            health_status["redis"] = "healthy"
        else:
            health_status["redis"] = "unhealthy"
            is_ready = False
    except Exception as e:
        logger.warning(f"Readiness check redis failure: {str(e)}")
        health_status["redis"] = f"unhealthy: {str(e)}"
        is_ready = False

    if not is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not_ready", "services": health_status},
        )

    return {"status": "ready", "services": health_status}
