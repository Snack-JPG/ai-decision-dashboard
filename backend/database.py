import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base

# Database URL - use SQLite file in the current directory
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_dashboard.db")

# Create engine with proper SQLite configuration
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database with tables"""
    print("Creating database tables...")
    create_tables()
    print("Database initialized successfully!")

# Helper function to get a database session
def get_db_session() -> Session:
    """Get a database session for use outside of FastAPI dependency injection"""
    return SessionLocal()
