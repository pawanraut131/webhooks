from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Create the SQLAlchemy engine. 
# This is the core interface to the PostgreSQL database.
engine = create_engine(settings.DATABASE_URL)

# Create a sessionmaker factory.
# A Session establishes a conversational workspace for the database.
# 'autocommit=False' means we manually call session.commit()
# 'autoflush=False' means we manage when changes are sent to the DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for our models.
# All SQLAlchemy models will inherit from this Base.
Base = declarative_base()

def get_db():
    """
    Dependency function to get a database session for a request.
    It yields the session and ensures it is closed after the request is done.
    This is used in FastAPI endpoint definitions.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
