import uuid
from typing import List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.dependencies import get_current_user, require_org_role
from app.models.user import User
from app.models.membership import RoleEnum
from app.schemas.api_key import APIKeyCreate, APIKeyCreatedResponse, APIKeyResponse
from app.services.api_key_service import APIKeyService

router = APIRouter(prefix="/api-keys", tags=["API Keys"])


@router.post("", response_model=APIKeyCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    request: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service_dep = require_org_role([RoleEnum.ADMIN, RoleEnum.OWNER])
    await service_dep(request.organization_id, current_user, db)

    service = APIKeyService(db)
    created_key = await service.create_api_key(request, creator_user_id=current_user.id)

    from app.services.audit_service import AuditService
    audit = AuditService(db)
    await audit.log_event(
        action="API_KEY_CREATED",
        resource_type="APIKey",
        organization_id=request.organization_id,
        user_id=current_user.id,
        resource_id=str(created_key.id),
        metadata={"name": request.name, "scopes": request.scopes}
    )

    return created_key


@router.get("", response_model=List[APIKeyResponse])
async def list_api_keys(
    organization_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service_dep = require_org_role([RoleEnum.ADMIN, RoleEnum.OWNER])
    await service_dep(organization_id, current_user, db)

    service = APIKeyService(db)
    return await service.list_api_keys(organization_id)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    id: uuid.UUID,
    organization_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service_dep = require_org_role([RoleEnum.ADMIN, RoleEnum.OWNER])
    await service_dep(organization_id, current_user, db)

    service = APIKeyService(db)
    await service.revoke_api_key(id, organization_id)

    from app.services.audit_service import AuditService
    audit = AuditService(db)
    await audit.log_event(
        action="API_KEY_REVOKED",
        resource_type="APIKey",
        organization_id=organization_id,
        user_id=current_user.id,
        resource_id=str(id),
    )

    return None
