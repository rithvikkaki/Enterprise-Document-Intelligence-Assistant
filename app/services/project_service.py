import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import NotFoundError
from app.models.project import Project
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse


class ProjectService:
    def __init__(self, session: AsyncSession):
        self.repo = ProjectRepository(session)

    async def create_project(self, org_id: uuid.UUID, request: ProjectCreate) -> ProjectResponse:
        project = Project(
            organization_id=org_id,
            name=request.name,
            description=request.description,
        )
        created = await self.repo.create(project)
        return ProjectResponse.model_validate(created)

    async def list_projects(self, org_id: uuid.UUID) -> List[ProjectResponse]:
        projects = await self.repo.list_by_org(org_id)
        return [ProjectResponse.model_validate(p) for p in projects]

    async def get_project(self, project_id: uuid.UUID, org_id: uuid.UUID) -> ProjectResponse:
        project = await self.repo.get_by_id(project_id, org_id)
        if not project:
            raise NotFoundError("Project", str(project_id))
        return ProjectResponse.model_validate(project)

    async def update_project(self, project_id: uuid.UUID, org_id: uuid.UUID, request: ProjectUpdate) -> ProjectResponse:
        project = await self.repo.get_by_id(project_id, org_id)
        if not project:
            raise NotFoundError("Project", str(project_id))
        if request.name is not None:
            project.name = request.name
        if request.description is not None:
            project.description = request.description
        updated = await self.repo.update(project)
        return ProjectResponse.model_validate(updated)

    async def delete_project(self, project_id: uuid.UUID, org_id: uuid.UUID) -> None:
        deleted = await self.repo.soft_delete(project_id, org_id)
        if not deleted:
            raise NotFoundError("Project", str(project_id))
