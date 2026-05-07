"""VoltPy database API facade."""

from __future__ import annotations

from dataclasses import dataclass
from importing.hook import import_real_module


@dataclass(slots=True)
class Database:
    """Small SQLAlchemy-backed database facade for future expansion."""

    connection_string: str

    def create_engine(self):
        sqlalchemy = import_real_module("sqlalchemy")
        return sqlalchemy.create_engine(self.connection_string)
