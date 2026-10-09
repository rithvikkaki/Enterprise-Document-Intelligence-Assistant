import uuid
from typing import Optional, List, Tuple
from sqlalchemy import select, update, delete
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.organization import Organization
from app.models.membership import Membership, RoleEnum
from app.models.user import User


class OrganizationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, org: Organization) -> Organization:
        self.session.add(org)
        await self.session.flush()
        return org

    async def get_by_id(self, org_id: uuid.UUID) -> Optional[Organization]:
        result = await self.session.execute(
            select(Organization).where(Organization.id == org_id, Organization.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Organization]:
        result = await self.session.execute(
            select(Organization).where(Organization.slug == slug, Organization.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: uuid.UUID) -> List[Tuple[Organization, RoleEnum]]:
        stmt = (
            select(Organization, Membership.role)
            .join(Membership, Membership.organization_id == Organization.id)
            .where(Membership.user_id == user_id, Organization.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        return result.all()

    async def add_member(self, membership: Membership) -> Membership:
        self.session.add(membership)
        await self.session.flush()
        return membership

    async def get_membership(self, org_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Membership]:
        stmt = select(Membership).where(
            Membership.organization_id == org_id,
            Membership.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_members(self, org_id: uuid.UUID) -> List[Tuple[Membership, User]]:
        stmt = (
            select(Membership, User)
            .join(User, Membership.user_id == User.id)
            .where(Membership.organization_id == org_id)
        )
        result = await self.session.execute(stmt)
        return result.all()

    async def update_member_role(self, member_id: uuid.UUID, role: RoleEnum) -> Optional[Membership]:
        stmt = select(Membership).where(Membership.id == member_id)
        result = await self.session.execute(stmt)
        mem = result.scalar_one_or_none()
        if mem:
            mem.role = role
            await self.session.flush()
        return mem

    async def remove_member(self, member_id: uuid.UUID) -> bool:
        stmt = delete(Membership).where(Membership.id == member_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0
