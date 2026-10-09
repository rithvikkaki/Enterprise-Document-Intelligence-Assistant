import uuid
from typing import List, Callable
from fastapi import Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import decode_token
from app.core.exceptions import AuthenticationError, PermissionDeniedError, TenantIsolationError
from app.db.session import get_db
from app.models.user import User
from app.models.membership import RoleEnum, Membership
from app.repositories.user_repository import UserRepository
from app.repositories.organization_repository import OrganizationRepository

security_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload.get("type") != "access":
        raise AuthenticationError("Invalid token type")
        
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AuthenticationError("Invalid token subject")

    repo = UserRepository(db)
    user = await repo.get_by_id(uuid.UUID(user_id_str))
    if not user or not user.is_active:
        raise AuthenticationError("User not found or inactive")
        
    return user


ROLE_HIERARCHY = {
    RoleEnum.OWNER: 4,
    RoleEnum.ADMIN: 3,
    RoleEnum.EDITOR: 2,
    RoleEnum.VIEWER: 1,
}


def require_org_role(allowed_roles: List[RoleEnum]):
    """Returns a dependency function verifying that current user has one of allowed_roles in specified org_id."""
    async def dependency(
        organization_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> Membership:
        org_repo = OrganizationRepository(db)
        membership = await org_repo.get_membership(organization_id, current_user.id)
        if not membership:
            raise TenantIsolationError("User is not a member of this organization")

        # Check hierarchy permission level
        user_level = ROLE_HIERARCHY.get(membership.role, 0)
        required_min_level = min([ROLE_HIERARCHY.get(r, 99) for r in allowed_roles])

        if user_level < required_min_level:
            raise PermissionDeniedError(
                f"Requires {allowed_roles} permission in organization. Current role: {membership.role.value}"
            )

        return membership

    return dependency
