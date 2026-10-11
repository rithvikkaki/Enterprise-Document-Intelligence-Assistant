from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings

# If using Supabase / PgBouncer connection pooling, disable asyncpg prepared statement caching
connect_args = {}
if "pooler.supabase.com" in settings.DATABASE_URL or "pgbouncer" in settings.DATABASE_URL.lower():
    connect_args["prepared_statement_cache_size"] = 0
    connect_args["statement_cache_size"] = 0

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10,
    connect_args=connect_args,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
