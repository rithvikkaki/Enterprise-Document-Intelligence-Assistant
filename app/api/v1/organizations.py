import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.dependencies import get_current_user, require_org_role
from app.models.user import User
from app.models.membership import RoleEnum
from app.schemas.organization import (
    OrganizationCreate, OrganizationResponse, MemberCreate, MemberUpdate, MemberResponse, OrganizationStatsResponse
)
from app.services.organization_service import OrganizationService

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get("/{organization_id}/stats", response_model=OrganizationStatsResponse)
async def get_organization_stats(
    organization_id: uuid.UUID,
    membership=Depends(require_org_role([RoleEnum.VIEWER, RoleEnum.EDITOR, RoleEnum.ADMIN, RoleEnum.OWNER])),
    db: AsyncSession = Depends(get_db),
):
    service = OrganizationService(db)
    return await service.get_organization_stats(organization_id)



@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    request: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = OrganizationService(db)
    return await service.create_organization(request, creator_user_id=current_user.id)


@router.get("", response_model=List[OrganizationResponse])
async def list_organizations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = OrganizationService(db)
    return await service.list_user_organizations(current_user.id)


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: uuid.UUID,
    membership=Depends(require_org_role([RoleEnum.VIEWER, RoleEnum.EDITOR, RoleEnum.ADMIN, RoleEnum.OWNER])),
    db: AsyncSession = Depends(get_db),
):
    service = OrganizationService(db)
    return await service.get_organization(organization_id)


@router.post("/{organization_id}/members", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
async def add_member(
    organization_id: uuid.UUID,
    request: MemberCreate,
    membership=Depends(require_org_role([RoleEnum.ADMIN, RoleEnum.OWNER])),
    db: AsyncSession = Depends(get_db),
):
    service = OrganizationService(db)
    return await service.add_member(organization_id, request)


@router.get("/{organization_id}/members", response_model=List[MemberResponse])
async def list_members(
    organization_id: uuid.UUID,
    membership=Depends(require_org_role([RoleEnum.VIEWER, RoleEnum.EDITOR, RoleEnum.ADMIN, RoleEnum.OWNER])),
    db: AsyncSession = Depends(get_db),
):
    service = OrganizationService(db)
    return await service.list_members(organization_id)


@router.patch("/{organization_id}/members/{member_id}", response_model=MemberResponse)
async def update_member(
    organization_id: uuid.UUID,
    member_id: uuid.UUID,
    request: MemberUpdate,
    membership=Depends(require_org_role([RoleEnum.ADMIN, RoleEnum.OWNER])),
    db: AsyncSession = Depends(get_db),
):
    service = OrganizationService(db)
    return await service.update_member_role(member_id, request)


@router.delete("/{organization_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    organization_id: uuid.UUID,
    member_id: uuid.UUID,
    membership=Depends(require_org_role([RoleEnum.ADMIN, RoleEnum.OWNER])),
    db: AsyncSession = Depends(get_db),
):
    service = OrganizationService(db)
    await service.remove_member(member_id)
    return None
