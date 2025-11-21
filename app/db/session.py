from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
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


# Dependency to get DB session
async def get_db() -> AsyncGenerator[AsyncSession , None]:
    """
    Provides a database session.
    Commit and rollback should be handled explicitly in service layer.
    
    Example:
        @app.post("/items/")
        async def create_item(item: ItemCreate, db: AsyncSession = Depends(get_db)):
            try:
                result = await item_service.create(db, item)
                await db.commit()
                return result
            except Exception as e:
                await db.rollback()
                raise
    """
    async with AsyncSessionLocal() as session:
        yield session
        
