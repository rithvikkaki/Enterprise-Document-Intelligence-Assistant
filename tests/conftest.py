import os
import asyncio
import pytest
import pytest_asyncio

os.environ["TESTING"] = "true"

from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.security import hash_password, create_access_token
from app.models.user import User
from app.models.organization import Organization
from app.models.membership import Membership, RoleEnum
from app.models.project import Project

# In-memory SQLite async database engine for ultra-fast, isolated testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user_a(db_session: AsyncSession) -> User:
    user = User(
        email="usera@org-a.com",
        hashed_password=hash_password("Password123!"),
        full_name="User Alpha",
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def user_b(db_session: AsyncSession) -> User:
    user = User(
        email="userb@org-b.com",
        hashed_password=hash_password("Password123!"),
        full_name="User Beta",
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def org_a(db_session: AsyncSession, user_a: User) -> Organization:
    org = Organization(name="Organization Alpha", slug="org-alpha")
    db_session.add(org)
    await db_session.flush()

    mem = Membership(user_id=user_a.id, organization_id=org.id, role=RoleEnum.OWNER)
    db_session.add(mem)
    await db_session.flush()
    return org


@pytest_asyncio.fixture
async def org_b(db_session: AsyncSession, user_b: User) -> Organization:
    org = Organization(name="Organization Beta", slug="org-beta")
    db_session.add(org)
    await db_session.flush()

    mem = Membership(user_id=user_b.id, organization_id=org.id, role=RoleEnum.OWNER)
    db_session.add(mem)
    await db_session.flush()
    return org


@pytest_asyncio.fixture
async def auth_headers_a(user_a: User) -> dict:
    token = create_access_token(str(user_a.id))
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def auth_headers_b(user_b: User) -> dict:
    token = create_access_token(str(user_b.id))
    return {"Authorization": f"Bearer {token}"}
