"""
Database configuration and setup for Maveric MiniPilot.

This module provides:
- SQLAlchemy engine and session factory
- Base class for declarative models
- Database URL configuration from environment variables
- Session management utilities
"""

import os
from contextlib import contextmanager
from typing import Generator, Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import StaticPool


# Base class for all declarative models
Base = declarative_base()


def get_database_url() -> str:
    """
    Get database URL from environment variable or use default.
    
    Priority:
    1. DATABASE_URL environment variable (full connection string)
    2. Constructed from individual components (DB_HOST, DB_PORT, etc.)
    3. Default SQLite for development
    
    Returns:
        Database connection URL string
    """
    # Check for full DATABASE_URL first
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url
    
    # Try to construct PostgreSQL URL from components
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "maveric_minipilot")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "")
    
    # If DB_HOST is set, assume PostgreSQL
    if os.getenv("DB_HOST"):
        if db_password:
            return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        else:
            return f"postgresql://{db_user}@{db_host}:{db_port}/{db_name}"
    
    # Default: SQLite for development
    db_path = os.getenv("DB_PATH", "data/maveric_minipilot.db")
    return f"sqlite:///{db_path}"


def create_database_engine(url: Optional[str] = None) -> Engine:
    """
    Create SQLAlchemy engine with appropriate configuration.
    
    Args:
        url: Optional database URL. If not provided, uses get_database_url()
    
    Returns:
        Configured SQLAlchemy Engine
    """
    if url is None:
        url = get_database_url()
    
    # SQLite-specific configuration
    if url.startswith("sqlite"):
        engine = create_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=os.getenv("DB_ECHO", "false").lower() == "true"
        )
    else:
        # PostgreSQL configuration
        engine = create_engine(
            url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,  # Verify connections before using
            echo=os.getenv("DB_ECHO", "false").lower() == "true"
        )
    
    return engine


# Global engine instance (created on first import)
_engine: Optional[Engine] = None


def get_engine() -> Engine:
    """
    Get or create the global database engine.
    
    Returns:
        SQLAlchemy Engine instance
    """
    global _engine
    if _engine is None:
        _engine = create_database_engine()
    return _engine


# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=get_engine()
)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Get a database session context manager.
    
    Usage:
        with get_session() as session:
            user = session.query(User).first()
            # Session automatically commits on success, rolls back on exception
    
    Yields:
        SQLAlchemy Session
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def session_scope():
    """
    Alternative session context manager (alias for get_session).
    
    Usage:
        with session_scope() as session:
            # Use session
    
    Yields:
        SQLAlchemy Session
    """
    yield from get_session()


def init_db():
    """
    Initialize database by creating all tables.
    
    This should be called after models are imported.
    Typically used for development/testing.
    """
    from database import models  # Import models to register them with Base
    Base.metadata.create_all(bind=get_engine())
    print("Database tables created successfully")


def drop_db():
    """
    Drop all database tables.
    
    WARNING: This will delete all data!
    Use only for development/testing.
    """
    from database import models  # Import models to register them with Base
    Base.metadata.drop_all(bind=get_engine())
    print("Database tables dropped successfully")


def reset_db():
    """
    Reset database by dropping and recreating all tables.
    
    WARNING: This will delete all data!
    Use only for development/testing.
    """
    drop_db()
    init_db()
    print("Database reset successfully")

