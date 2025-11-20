from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import config

# Create async engine
# Note: Use postgresql+asyncpg for async support
DATABASE_URL = config.db_url.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(
    DATABASE_URL,
    echo=config.debug,  # Log SQL queries in debug mode
    future=True,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=10,  # Maximum number of connections to keep in the pool
    max_overflow=20,  # Maximum number of connections that can be created beyond pool_size
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Prevent attributes from expiring after commit
    autocommit=False,
    autoflush=False,
)

# Base class for declarative models
Base = declarative_base()


# Dependency to get DB session
async def get_db() -> AsyncSession:
    """
    Async generator that provides a database session.
    Use as a FastAPI dependency.

    Example:
        @app.get("/items/")
        async def read_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
