"""Database configuration and models."""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

# Database URL
DATABASE_URL = "sqlite+aiosqlite:///./ara.db"

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Base class
Base = declarative_base()


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Integer, default=1)


class Project(Base):
    """Project model."""

    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Paper(Base):
    """Paper model."""

    __tablename__ = "papers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    title = Column(String, nullable=False)
    authors = Column(JSON, default=list)
    abstract = Column(String, nullable=True)
    journal = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    doi = Column(String, nullable=True)
    source = Column(String, nullable=False)
    paper_type = Column(String, nullable=True)
    pdf_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PaperMatrix(Base):
    """Parsed paper data matrix."""

    __tablename__ = "paper_matrix"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    paper_id = Column(String, ForeignKey("papers.id"), nullable=False)
    research_type = Column(String, nullable=True)
    independent_vars = Column(JSON, default=list)
    dependent_vars = Column(JSON, default=list)
    mediating_vars = Column(JSON, default=list)
    moderating_vars = Column(JSON, default=list)
    sample_size = Column(Integer, nullable=True)
    subjects = Column(JSON, default=list)
    key_findings = Column(String, nullable=True)
    raw_json = Column(JSON, default=dict)


class Tracker(Base):
    """Tracker model for briefings."""

    __tablename__ = "trackers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    query = Column(String, nullable=False)
    frequency = Column(String, default="weekly")
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    last_run = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


async def get_db():
    """Get database session."""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
