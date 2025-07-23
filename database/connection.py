import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base
import logging

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/newsdb')

# Create engine
engine = create_engine(DATABASE_URL, echo=False)

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
    """Get database connection"""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        logging.error(f"Database connection failed: {str(e)}")
        db.close()
        raise
    finally:
        db.close()

def get_db():
    """Database dependency for FastAPI-style usage"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
