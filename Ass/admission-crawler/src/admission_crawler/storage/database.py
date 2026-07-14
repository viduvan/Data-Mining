"""
database.py — Database connection and session management.
"""

from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine

from admission_crawler.config import settings
from admission_crawler.storage.models import Base

_engine = None
_SessionFactory = None

def get_engine() -> Engine:
    """Get or create the SQLAlchemy engine."""
    global _engine
    if _engine is None:
        _engine = create_engine(
            settings.database.url,
            echo=settings.database.echo,
            connect_args={"check_same_thread": False} if settings.database.url.startswith("sqlite") else {}
        )
    return _engine

def init_db() -> None:
    """Initialize the database schema."""
    import os
    if settings.database.url.startswith("sqlite:///"):
        db_path = settings.database.url.replace("sqlite:///", "")
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
            
    engine = get_engine()
    Base.metadata.create_all(engine)

def get_session_factory() -> sessionmaker:
    """Get the session factory."""
    global _SessionFactory
    if _SessionFactory is None:
        _SessionFactory = sessionmaker(bind=get_engine())
    return _SessionFactory

@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
