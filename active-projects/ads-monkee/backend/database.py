"""
Database Setup
==============

SQLAlchemy configuration for PostgreSQL with async support.
"""

from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from backend.config import settings

# ============================================================================
# Base Class for Models
# ============================================================================

Base = declarative_base()

# ============================================================================
# Sync Engine (for Alembic migrations)
# ============================================================================

sync_engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.is_development,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using
    connect_args={
        "sslmode": "require",
        "connect_timeout": 10,
    },
)

SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)

# ============================================================================
# Async Engine (for FastAPI)
# ============================================================================

# Convert psycopg2 URL to asyncpg URL
async_database_url = settings.DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
).replace(
    "psycopg2://", "postgresql+asyncpg://"
)

async_engine = create_async_engine(
    async_database_url,
    echo=settings.is_development,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    connect_args={
        "ssl": "require",
        "timeout": 10,
    },
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# ============================================================================
# Database Session Dependency (FastAPI)
# ============================================================================


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides an async database session.
    
    Usage:
        @app.get("/clients")
        async def get_clients(db: AsyncSession = Depends(get_db)):
            ...
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_sync_db() -> Session:
    """
    Get synchronous database session (for Celery workers).
    
    Returns:
        Session: Sync database session
    """
    db = SyncSessionLocal()
    try:
        return db
    finally:
        db.close()


# ============================================================================
# Database Initialization
# ============================================================================


async def init_db() -> None:
    """
    Initialize database (create all tables).
    
    Note: In production, use Alembic migrations instead.
    This is for development/testing only.
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    """
    Drop all tables.
    
    **DANGER:** Only use in development/testing!
    """
    if settings.is_production:
        raise RuntimeError("Cannot drop database in production!")
    
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

