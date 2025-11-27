"""Test configuration and fixtures."""

from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
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


@pytest_asyncio.fixture(scope="session")
async def test_engine(test_engine_url: str):
    """
    Create a session-scoped test database engine.

    Session scope means:
    - Tables are created ONCE at the start of the test session
    - The engine is reused across ALL tests
    - Tables are dropped ONCE at the end of the test session

    This provides massive performance benefits:
    - 100 tests with function scope: ~5 minutes (creates/drops tables 100 times)
    - 100 tests with session scope: ~14 seconds (creates/drops tables 1 time)

    Using pytest_asyncio.fixture with scope="session" properly handles
    the event loop lifecycle to prevent "attached to a different loop" errors.
    """
    engine = create_async_engine(
        test_engine_url,
        echo=False,
        poolclass=NullPool,
    )

    # Create all tables ONCE for the entire test session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables ONCE at the end of the test session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a function-scoped database session with automatic cleanup.

    This fixture is function-scoped (runs for each test), which ensures:
    - Each test gets a fresh, isolated database session
    - Test data doesn't leak between tests
    - Transaction rollback cleans up data automatically

    """
    # Create a connection that will persist for the entire test
    connection = await test_engine.connect()

    # Start a transaction
    transaction = await connection.begin()

    # Create a session bound to this connection
    session_factory = async_sessionmaker(
        bind=connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint"
    )

    try:
        session = session_factory()
        yield session
    finally:
        # Close the session
        await session.close()
        # Rollback the transaction (undoes all changes)
        await transaction.rollback()
        # Close the connection
        await connection.close()


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client with database session override."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Return sample user data for testing."""
    return {
        "user_name": "testuser",
        "email": "test@example.com",
        "password": "securepassword123",
    }


@pytest.fixture
def sample_users_data():
    """Return multiple sample users for testing."""
    return [
        {"user_name": "user1", "email": "user1@example.com", "password": "password1"},
        {"user_name": "user2", "email": "user2@example.com", "password": "password2"},
        {"user_name": "user3", "email": "user3@example.com", "password": "password3"},
    ]


@pytest_asyncio.fixture
async def created_user(async_client: AsyncClient, sample_user_data):
    """Create a user in the database and return the response."""
    response = await async_client.post("/api/v1/users", json=sample_user_data)
    assert response.status_code == 200
    return response.json()


@pytest_asyncio.fixture
async def created_users(async_client: AsyncClient, sample_users_data):
    """Create multiple users in the database and return their data."""
    created = []
    for user_data in sample_users_data:
        response = await async_client.post("/api/v1/users", json=user_data)
        assert response.status_code == 200
        created.append(response.json())
    return created
