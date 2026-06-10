from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from config import settings

# Create SQLAlchemy engine
# Using StaticPool for SQLite to ensure connection reuse in-memory
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=settings.DEBUG  # Log all SQL statements in debug mode
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Session:
    """
    Dependency for FastAPI to get database session.
    Yields a database session for each request.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize the database by creating all tables.
    Should be called once at application startup.
    """
    # Import models to register them with Base.metadata
    from models import Base
    
    # Create all tables
    Base.metadata.create_all(bind=engine)