"""Test configuration and fixtures."""

import asyncio
import os
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.api.deps import get_db
from app.db.base import Base
from app.main import app


@pytest.fixture(scope="session")
def postgres_container():
    """Start a PostgreSQL test container for the session."""
    with PostgresContainer("postgres:15", driver="asyncpg") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def test_engine_url(postgres_container: PostgresContainer) -> str:
    """Get the test database URL from container."""
    # Get connection URL from container
    connection_url = postgres_container.get_connection_url()
    # Replace psycopg2 driver with asyncpg for async operations
    async_url = connection_url.replace("psycopg2", "asyncpg")
    return async_url


@pytest.fixture
async def test_engine(test_engine_url: str):
    """Create a test database engine using the PostgreSQL container."""
    engine = create_async_engine(
        test_engine_url,
        echo=False,
        pool_pre_ping=True,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session with automatic cleanup."""
    from sqlalchemy.ext.asyncio import async_sessionmaker
    
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()
        
        # Clean up all tables after each test
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(text(f"TRUNCATE TABLE {table.name} CASCADE"))
        await session.commit()


@pytest.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client with database session override."""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Return sample user data for testing."""
    return {
        "user_name": "testuser",
        "email": "test@example.com",
        "password": "securepassword123"
    }


@pytest.fixture
def sample_users_data():
    """Return multiple sample users for testing."""
    return [
        {
            "user_name": "user1",
            "email": "user1@example.com",
            "password": "password1"
        },
        {
            "user_name": "user2",
            "email": "user2@example.com",
            "password": "password2"
        },
        {
            "user_name": "user3",
            "email": "user3@example.com",
            "password": "password3"
        }
    ]


@pytest.fixture
async def created_user(async_client: AsyncClient, sample_user_data):
    """Create a user in the database and return the response."""
    response = await async_client.post("/api/v1/users", json=sample_user_data)
    assert response.status_code == 200
    return response.json()


@pytest.fixture
async def created_users(async_client: AsyncClient, sample_users_data):
    """Create multiple users in the database and return their data."""
    created = []
    for user_data in sample_users_data:
        response = await async_client.post("/api/v1/users", json=user_data)
        assert response.status_code == 200
        created.append(response.json())
    return created
