import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base
import logging

# Database configuration
DEFAULT_SQLITE_URL = 'sqlite:///./newsnexus.db'
DATABASE_URL = os.getenv('DATABASE_URL', DEFAULT_SQLITE_URL)


def _create_engine(database_url: str):
    """Create a SQLAlchemy engine with sensible local defaults."""
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, echo=False, connect_args=connect_args)

# Create engine
engine = _create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logging.info("Database initialized successfully")
    except Exception as e:
        logging.error(f"Database initialization failed: {str(e)}")
        raise

def get_db_connection():
    """Get a database session.

    Caller is responsible for calling ``db.close()`` when done.
    """
    return SessionLocal()

def get_db():
    """Database dependency for FastAPI-style usage"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
