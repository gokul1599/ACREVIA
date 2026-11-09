"""
ACREVIA - Database Session & Connection Lifecycle.
"""

import ssl
from typing import Generator
from urllib.parse import urlparse, urlunparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.database.rls import clear_tenant_context

# Configure engine with connection pooling and SQLite / PostgreSQL compatibility
connect_args = {}
pool_kwargs = {}
db_url = settings.DATABASE_URL

if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    if ":memory:" in db_url:
        pool_kwargs = {"poolclass": StaticPool}
else:
    # Check if psycopg (v3) is loadable without DLL/Application Control blocks
    use_pg8000 = False
    try:
        import psycopg
        from psycopg import pq
    except (ImportError, Exception):
        use_pg8000 = True

    if use_pg8000 or "+pg8000" in db_url:
        # Normalize to postgresql+pg8000:// without unsupported query parameters
        parsed = urlparse(db_url)
        db_url = urlunparse((
            "postgresql+pg8000",
            parsed.netloc,
            parsed.path,
            parsed.params,
            "",
            parsed.fragment
        ))
        connect_args["ssl_context"] = ssl.create_default_context()
    elif db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    # PostgreSQL pooling parameters
    pool_kwargs = {
        "pool_size": settings.DATABASE_POOL_SIZE,
        "max_overflow": settings.DATABASE_MAX_OVERFLOW,
        "pool_pre_ping": True,
    }

engine = create_engine(
    db_url,
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
        clear_tenant_context(db)
        db.close()
