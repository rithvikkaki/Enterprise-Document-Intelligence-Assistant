import uuid
from typing import Optional, Dict, Any, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogResponse


class AuditService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def log_event(
        self,
        action: str,
        resource_type: str,
        organization_id: Optional[uuid.UUID] = None,
        user_id: Optional[uuid.UUID] = None,
        resource_id: Optional[str] = None,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        # Exclude any secrets or sensitive fields before logging
        safe_meta = dict(metadata or {})
        for secret_key in ["password", "secret", "token", "key"]:
            safe_meta.pop(secret_key, None)

        log = AuditLog(
            organization_id=organization_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            request_id=request_id,
            ip_address=ip_address,
            metadata_json=safe_meta,
        )
        self.session.add(log)
        await self.session.flush()
        return log

    async def list_org_audit_logs(self, org_id: uuid.UUID, limit: int = 50) -> List[AuditLogResponse]:
        stmt = (
            select(AuditLog)
            .where(AuditLog.organization_id == org_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        logs = result.scalars().all()
        return [AuditLogResponse.model_validate(l) for l in logs]
