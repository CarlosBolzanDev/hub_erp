"""Database configuration helpers for the catalog/kit merge layer."""

from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    """Shared SQLAlchemy declarative base."""


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///hub_erp.db")

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
