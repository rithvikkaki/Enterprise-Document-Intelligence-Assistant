import uuid
from typing import Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.exceptions import AuthenticationError, ConflictError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse


class AuthService:
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)

    async def register(self, request: RegisterRequest) -> UserResponse:
        existing = await self.user_repo.get_by_email(request.email)
        if existing:
            raise ConflictError("User with this email already exists")

        user = User(
            email=request.email,
            hashed_password=hash_password(request.password),
            full_name=request.full_name,
        )
        created_user = await self.user_repo.create(user)
        return UserResponse.model_validate(created_user)

    async def login(self, request: LoginRequest) -> TokenResponse:
        user = await self.user_repo.get_by_email(request.email)
        if not user or not verify_password(request.password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")
        if not user.is_active:
            raise AuthenticationError("User account is inactive")

        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise AuthenticationError("Invalid refresh token")

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise AuthenticationError("Invalid token subject")

        user = await self.user_repo.get_by_id(uuid.UUID(user_id_str))
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive")

        new_access_token = create_access_token(str(user.id))
        new_refresh_token = create_refresh_token(str(user.id))
        return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token)
