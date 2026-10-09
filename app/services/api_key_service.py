import uuid
import secrets
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password, verify_password
from app.core.exceptions import AuthenticationError, NotFoundError, PermissionDeniedError
from app.models.api_key import APIKey
from app.schemas.api_key import APIKeyCreate, APIKeyCreatedResponse, APIKeyResponse


class APIKeyService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_api_key(self, request: APIKeyCreate, creator_user_id: uuid.UUID) -> APIKeyCreatedResponse:
        prefix = secrets.token_hex(4)  # 8 char random hex prefix
        secret = secrets.token_urlsafe(32)  # 43 char secret
        full_key = f"edip_live_{prefix}_{secret}"
        
        # Secure Argon2 password hashing of secret
        hashed_secret = hash_password(secret)

        expires_at = None
        if request.expires_in_days:
            expires_at = datetime.now(timezone.utc) + timedelta(days=request.expires_in_days)

        api_key = APIKey(
            organization_id=request.organization_id,
            name=request.name,
            key_prefix=prefix,
            hashed_key=hashed_secret,
            scopes=request.scopes or ["read", "write"],
            created_by_id=creator_user_id,
            expires_at=expires_at,
        )
        self.session.add(api_key)
        await self.session.flush()

        return APIKeyCreatedResponse(
            id=api_key.id,
            organization_id=api_key.organization_id,
            name=api_key.name,
            key_prefix=prefix,
            secret_key=full_key,  # Raw secret returned ONLY ONCE upon creation
            scopes=api_key.scopes or [],
            expires_at=expires_at,
            created_at=api_key.created_at,
        )

    async def authenticate_key(self, raw_key: str, required_scope: Optional[str] = None) -> APIKey:
        """Authenticate full key `edip_live_<prefix>_<secret>` via prefix lookup & Argon2 verification."""
        if not raw_key.startswith("edip_live_"):
            raise AuthenticationError("Invalid API key format")

        parts = raw_key.split("_")
        if len(parts) < 4:
            raise AuthenticationError("Invalid API key format")

        prefix = parts[2]
        secret = "_".join(parts[3:])

        # Efficient database lookup by prefix
        stmt = select(APIKey).where(APIKey.key_prefix == prefix)
        result = await self.session.execute(stmt)
        api_key = result.scalar_one_or_none()

        if not api_key:
            raise AuthenticationError("Invalid API key prefix")

        # Argon2 verification of secret
        if not verify_password(secret, api_key.hashed_key):
            raise AuthenticationError("Invalid API key secret")

        now = datetime.now(timezone.utc)
        if api_key.revoked_at:
            raise AuthenticationError("API key has been revoked")

        if api_key.expires_at and api_key.expires_at < now:
            raise AuthenticationError("API key has expired")

        if required_scope and api_key.scopes:
            if required_scope not in api_key.scopes:
                raise PermissionDeniedError(f"API key missing required scope: '{required_scope}'")

        return api_key

    async def list_api_keys(self, org_id: uuid.UUID) -> List[APIKeyResponse]:
        stmt = (
            select(APIKey)
            .where(APIKey.organization_id == org_id, APIKey.revoked_at.is_(None))
            .order_by(APIKey.created_at.desc())
        )
        result = await self.session.execute(stmt)
        keys = result.scalars().all()
        return [APIKeyResponse.model_validate(k) for k in keys]

    async def revoke_api_key(self, key_id: uuid.UUID, org_id: uuid.UUID) -> None:
        stmt = select(APIKey).where(APIKey.id == key_id, APIKey.organization_id == org_id)
        res = await self.session.execute(stmt)
        key = res.scalar_one_or_none()
        if not key:
            raise NotFoundError("APIKey", str(key_id))

        key.revoked_at = datetime.now(timezone.utc)
        await self.session.flush()
