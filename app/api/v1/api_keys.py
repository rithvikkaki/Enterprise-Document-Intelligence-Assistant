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
    return await service.create_api_key(request, creator_user_id=current_user.id)


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
    return None
