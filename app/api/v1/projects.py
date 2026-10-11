import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.dependencies import get_current_user, require_org_role
from app.models.user import User
from app.models.membership import RoleEnum
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.services.project_service import ProjectService
from app.core.exceptions import ValidationError

router = APIRouter(prefix="", tags=["Projects"])


@router.post("/organizations/{organization_id}/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    organization_id: uuid.UUID,
    request: ProjectCreate,
    membership=Depends(require_org_role([RoleEnum.EDITOR, RoleEnum.ADMIN, RoleEnum.OWNER])),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    proj = await service.create_project(organization_id, request)

    from app.services.audit_service import AuditService
    audit = AuditService(db)
    await audit.log_event(
        action="PROJECT_CREATED",
        resource_type="Project",
        organization_id=organization_id,
        user_id=getattr(membership, "user_id", None),
        resource_id=str(proj.id),
        metadata={"name": proj.name}
    )

    return proj


@router.get("/organizations/{organization_id}/projects", response_model=List[ProjectResponse])
async def list_projects(
    organization_id: uuid.UUID,
    membership=Depends(require_org_role([RoleEnum.VIEWER, RoleEnum.EDITOR, RoleEnum.ADMIN, RoleEnum.OWNER])),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    return await service.list_projects(organization_id)


# Support direct /projects routes for flexibility (via Query param or X-Organization-ID header)
@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project_direct(
    request: ProjectCreate,
    organization_id: Optional[uuid.UUID] = Query(None),
    x_organization_id: Optional[uuid.UUID] = Header(None, alias="X-Organization-ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    org_id = organization_id or x_organization_id
    if not org_id:
        raise ValidationError("organization_id query parameter or X-Organization-ID header is required")
    service_dep = require_org_role([RoleEnum.EDITOR, RoleEnum.ADMIN, RoleEnum.OWNER])
    await service_dep(org_id, current_user, db)
    service = ProjectService(db)
    proj = await service.create_project(org_id, request)

    from app.services.audit_service import AuditService
    audit = AuditService(db)
    await audit.log_event(
        action="PROJECT_CREATED",
        resource_type="Project",
        organization_id=org_id,
        user_id=current_user.id,
        resource_id=str(proj.id),
        metadata={"name": proj.name}
    )

    return proj


@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects_direct(
    organization_id: Optional[uuid.UUID] = Query(None),
    x_organization_id: Optional[uuid.UUID] = Header(None, alias="X-Organization-ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    org_id = organization_id or x_organization_id
    if not org_id:
        raise ValidationError("organization_id query parameter or X-Organization-ID header is required")
    service_dep = require_org_role([RoleEnum.VIEWER, RoleEnum.EDITOR, RoleEnum.ADMIN, RoleEnum.OWNER])
    await service_dep(org_id, current_user, db)
    service = ProjectService(db)
    return await service.list_projects(org_id)


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None),
    x_organization_id: Optional[uuid.UUID] = Header(None, alias="X-Organization-ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    org_id = organization_id or x_organization_id
    if not org_id:
        raise ValidationError("organization_id query parameter or X-Organization-ID header is required")
    service_dep = require_org_role([RoleEnum.VIEWER, RoleEnum.EDITOR, RoleEnum.ADMIN, RoleEnum.OWNER])
    await service_dep(org_id, current_user, db)
    service = ProjectService(db)
    return await service.get_project(project_id, org_id)


@router.patch("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    request: ProjectUpdate,
    organization_id: Optional[uuid.UUID] = Query(None),
    x_organization_id: Optional[uuid.UUID] = Header(None, alias="X-Organization-ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    org_id = organization_id or x_organization_id
    if not org_id:
        raise ValidationError("organization_id query parameter or X-Organization-ID header is required")
    service_dep = require_org_role([RoleEnum.EDITOR, RoleEnum.ADMIN, RoleEnum.OWNER])
    await service_dep(org_id, current_user, db)
    service = ProjectService(db)
    return await service.update_project(project_id, org_id, request)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None),
    x_organization_id: Optional[uuid.UUID] = Header(None, alias="X-Organization-ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    org_id = organization_id or x_organization_id
    if not org_id:
        raise ValidationError("organization_id query parameter or X-Organization-ID header is required")
    service_dep = require_org_role([RoleEnum.ADMIN, RoleEnum.OWNER])
    await service_dep(org_id, current_user, db)
    service = ProjectService(db)
    await service.delete_project(project_id, org_id)
    return None
