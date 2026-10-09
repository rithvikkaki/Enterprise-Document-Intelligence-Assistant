import uuid
import re
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import ConflictError, NotFoundError, PermissionDeniedError
from app.models.organization import Organization
from app.models.membership import Membership, RoleEnum
from app.models.user import User
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.organization import (
    OrganizationCreate, OrganizationUpdate, OrganizationResponse,
    MemberCreate, MemberUpdate, MemberResponse
)


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s_-]+", "-", text)


class OrganizationService:
    def __init__(self, session: AsyncSession):
        self.org_repo = OrganizationRepository(session)
        self.user_repo = UserRepository(session)

    async def create_organization(self, request: OrganizationCreate, creator_user_id: uuid.UUID) -> OrganizationResponse:
        slug = request.slug or slugify(request.name)
        existing = await self.org_repo.get_by_slug(slug)
        if existing:
            # Append random suffix if slug exists
            slug = f"{slug}-{uuid.uuid4().hex[:6]}"

        org = Organization(name=request.name, slug=slug)
        created_org = await self.org_repo.create(org)

        # Creator becomes OWNER
        membership = Membership(
            user_id=creator_user_id,
            organization_id=created_org.id,
            role=RoleEnum.OWNER,
        )
        await self.org_repo.add_member(membership)

        return OrganizationResponse.model_validate(created_org)

    async def get_organization(self, org_id: uuid.UUID) -> OrganizationResponse:
        org = await self.org_repo.get_by_id(org_id)
        if not org:
            raise NotFoundError("Organization", str(org_id))
        return OrganizationResponse.model_validate(org)

    async def list_user_organizations(self, user_id: uuid.UUID) -> List[OrganizationResponse]:
        results = await self.org_repo.list_by_user(user_id)
        return [OrganizationResponse.model_validate(org) for org, role in results]

    async def add_member(self, org_id: uuid.UUID, request: MemberCreate) -> MemberResponse:
        user = await self.user_repo.get_by_email(request.email)
        if not user:
            raise NotFoundError("User with email", request.email)

        existing_mem = await self.org_repo.get_membership(org_id, user.id)
        if existing_mem:
            raise ConflictError("User is already a member of this organization")

        mem = Membership(
            user_id=user.id,
            organization_id=org_id,
            role=request.role,
        )
        created_mem = await self.org_repo.add_member(mem)
        return MemberResponse(
            id=created_mem.id,
            user_id=user.id,
            organization_id=org_id,
            role=created_mem.role,
            user_email=user.email,
            user_full_name=user.full_name,
            created_at=created_mem.created_at,
        )

    async def list_members(self, org_id: uuid.UUID) -> List[MemberResponse]:
        members_with_users = await self.org_repo.list_members(org_id)
        return [
            MemberResponse(
                id=mem.id,
                user_id=user.id,
                organization_id=org_id,
                role=mem.role,
                user_email=user.email,
                user_full_name=user.full_name,
                created_at=mem.created_at,
            )
            for mem, user in members_with_users
        ]

    async def update_member_role(self, member_id: uuid.UUID, request: MemberUpdate) -> MemberResponse:
        mem = await self.org_repo.update_member_role(member_id, request.role)
        if not mem:
            raise NotFoundError("Membership", str(member_id))

        user = await self.user_repo.get_by_id(mem.user_id)
        return MemberResponse(
            id=mem.id,
            user_id=mem.user_id,
            organization_id=mem.organization_id,
            role=mem.role,
            user_email=user.email if user else "",
            user_full_name=user.full_name if user else "",
            created_at=mem.created_at,
        )

    async def remove_member(self, member_id: uuid.UUID) -> None:
        success = await self.org_repo.remove_member(member_id)
        if not success:
            raise NotFoundError("Membership", str(member_id))

    async def get_organization_stats(self, org_id: uuid.UUID) -> dict:
        from sqlalchemy import select, func, case
        from app.models.document import Document, ProcessingStatusEnum
        from app.models.project import Project

        doc_stmt = (
            select(
                func.count(Document.id).label("total_documents"),
                func.count(case((Document.status == ProcessingStatusEnum.COMPLETED, 1))).label("completed_documents"),
                func.count(case((Document.status == ProcessingStatusEnum.PROCESSING, 1))).label("processing_documents"),
                func.count(case((Document.status == ProcessingStatusEnum.FAILED, 1))).label("failed_documents"),
            )
            .where(Document.organization_id == org_id)
        )
        doc_res = await self.org_repo.session.execute(doc_stmt)
        doc_row = doc_res.one()

        proj_stmt = select(func.count(Project.id)).where(Project.organization_id == org_id)
        proj_res = await self.org_repo.session.execute(proj_stmt)
        total_projects = proj_res.scalar() or 0

        members_with_users = await self.org_repo.list_members(org_id)
        total_members = len(members_with_users)

        return {
            "total_documents": doc_row.total_documents or 0,
            "completed_documents": doc_row.completed_documents or 0,
            "processing_documents": doc_row.processing_documents or 0,
            "failed_documents": doc_row.failed_documents or 0,
            "total_projects": total_projects,
            "total_members": total_members,
        }

