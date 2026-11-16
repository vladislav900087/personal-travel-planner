from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.infrastructure.database import get_db
from app.main import app
from app.models.base import Base
from app.repositories.user_repository import UserRepository
from app.repositories.token_repository import TokenRepository

# async engine for testing using NullPool (prevents connection sharing across loops)
test_engine = create_async_engine(
    settings.test_database_url,
    poolclass=pool.NullPool,
    echo=False,
)

test_session_maker = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(autouse=True)
async def setup_test_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# isolated db session for each test
@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_session_maker() as session:
        yield session


# test client with get_db overridden to use test session
@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()

@pytest.fixture
def user_repo(db_session):
    return UserRepository(db_session)

@pytest.fixture
def token_repo(db_session):
    return TokenRepository(db_session)
