import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.dependencies import require_org_role
from app.models.membership import RoleEnum
from app.schemas.audit_log import AuditLogResponse
from app.services.audit_service import AuditService

router = APIRouter(prefix="/organizations/{organization_id}/audit-logs", tags=["Audit Logs"])


@router.get("", response_model=List[AuditLogResponse])
async def list_audit_logs(
    organization_id: uuid.UUID,
    limit: int = Query(default=50, ge=1, le=200),
    membership=Depends(require_org_role([RoleEnum.VIEWER, RoleEnum.EDITOR, RoleEnum.ADMIN, RoleEnum.OWNER])),
    db: AsyncSession = Depends(get_db),
):
    service = AuditService(db)
    return await service.list_org_audit_logs(org_id=organization_id, limit=limit)
