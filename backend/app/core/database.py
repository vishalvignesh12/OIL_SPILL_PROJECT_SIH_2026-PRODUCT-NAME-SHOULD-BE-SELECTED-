from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from app.core.config import settings

# Create async engine with PostGIS-aware parameters
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    """Dependency for injecting db session in FastAPI endpoints."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def check_db_health() -> bool:
    """Check database health by executing a simple query."""
    try:
        async with AsyncSessionLocal() as session:
            # Query postgis version to verify both PostgreSQL and PostGIS are healthy
            await session.execute(text("SELECT PostGIS_Full_Version();"))
            await session.commit()
            return True
    except Exception:
        return False
