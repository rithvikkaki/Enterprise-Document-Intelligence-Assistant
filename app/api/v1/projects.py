import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.dependencies import get_current_user, require_org_role
from app.models.membership import RoleEnum
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.services.project_service import ProjectService

router = APIRouter(prefix="", tags=["Projects"])


@router.post("/organizations/{organization_id}/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    organization_id: uuid.UUID,
    request: ProjectCreate,
    membership=Depends(require_org_role([RoleEnum.EDITOR, RoleEnum.ADMIN, RoleEnum.OWNER])),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    return await service.create_project(organization_id, request)


@router.get("/organizations/{organization_id}/projects", response_model=List[ProjectResponse])
async def list_projects(
    organization_id: uuid.UUID,
    membership=Depends(require_org_role([RoleEnum.VIEWER, RoleEnum.EDITOR, RoleEnum.ADMIN, RoleEnum.OWNER])),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    return await service.list_projects(organization_id)


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    organization_id: uuid.UUID,
    membership=Depends(require_org_role([RoleEnum.VIEWER, RoleEnum.EDITOR, RoleEnum.ADMIN, RoleEnum.OWNER])),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    return await service.get_project(project_id, organization_id)


@router.patch("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    organization_id: uuid.UUID,
    request: ProjectUpdate,
    membership=Depends(require_org_role([RoleEnum.EDITOR, RoleEnum.ADMIN, RoleEnum.OWNER])),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    return await service.update_project(project_id, organization_id, request)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: uuid.UUID,
    organization_id: uuid.UUID,
    membership=Depends(require_org_role([RoleEnum.ADMIN, RoleEnum.OWNER])),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    await service.delete_project(project_id, organization_id)
    return None
