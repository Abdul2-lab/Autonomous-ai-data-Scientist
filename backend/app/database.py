"""
SQLAlchemy engine/session setup. SQLite for local dev, swappable to Postgres
by changing DATABASE_URL only (no code changes required).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Called once at application startup."""
    # Import models so they are registered on Base.metadata before create_all.
    from app.models import dataset, analysis, model_experiment, report  # noqa: F401

    Base.metadata.create_all(bind=engine)
