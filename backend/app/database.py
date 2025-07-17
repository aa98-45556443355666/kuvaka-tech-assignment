"""
Database configuration for SQLAlchemy engine, session, and base model.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)  # Create SQLAlchemy engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # Session factory
Base = declarative_base()  # Base class for models 