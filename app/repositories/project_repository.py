import uuid
from typing import Optional, List
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.project import Project


class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, project: Project) -> Project:
        self.session.add(project)
        await self.session.flush()
        return project

    async def get_by_id(self, project_id: uuid.UUID, org_id: uuid.UUID) -> Optional[Project]:
        # Enforce tenant isolation in database query
        stmt = select(Project).where(
            Project.id == project_id,
            Project.organization_id == org_id,
            Project.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_org(self, org_id: uuid.UUID) -> List[Project]:
        stmt = select(Project).where(
            Project.organization_id == org_id,
            Project.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, project: Project) -> Project:
        await self.session.flush()
        return project

    async def soft_delete(self, project_id: uuid.UUID, org_id: uuid.UUID) -> bool:
        project = await self.get_by_id(project_id, org_id)
        if project:
            from datetime import datetime, timezone
            project.deleted_at = datetime.now(timezone.utc)
            await self.session.flush()
            return True
        return False
