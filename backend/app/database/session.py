"""
ACREVIA - Database Session & Connection Lifecycle.
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from backend.app.core.config import settings
from backend.app.core.logging import logger

# Configure engine with connection pooling and SQLite compatibility
connect_args = {}
pool_kwargs = {}

if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    if ":memory:" in settings.DATABASE_URL:
        pool_kwargs = {"poolclass": StaticPool}
else:
    # PostgreSQL pooling parameters
    pool_kwargs = {
        "pool_size": settings.DATABASE_POOL_SIZE,
        "max_overflow": settings.DATABASE_MAX_OVERFLOW,
        "pool_pre_ping": True,
    }

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    **pool_kwargs
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding a thread-safe database session.
    Automatically rolls back on uncaught exception and closes on completion.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database session rollback due to error: {e}")
        raise
    finally:
        db.close()
