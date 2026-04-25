"""ORM models for catalog records and normalized kit merge tables."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base


class CatalogRecord(Base):
    """Original catalog source-of-truth table (kept intact)."""

    __tablename__ = "catalog_record"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    montadora: Mapped[str | None] = mapped_column(Text, nullable=True)
    modelo: Mapped[str | None] = mapped_column(Text, nullable=True)
    motor: Mapped[str | None] = mapped_column(Text, nullable=True)
    ano_de: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ano_ate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    combustivel: Mapped[str | None] = mapped_column(Text, nullable=True)
    local_ar_cabine: Mapped[str | None] = mapped_column(Text, nullable=True)

    ar_1: Mapped[str | None] = mapped_column(Text, nullable=True)
    ar_2: Mapped[str | None] = mapped_column(Text, nullable=True)
    lubrificante_1: Mapped[str | None] = mapped_column(Text, nullable=True)
    lubrificante_2: Mapped[str | None] = mapped_column(Text, nullable=True)
    combustivel_1: Mapped[str | None] = mapped_column(Text, nullable=True)
    combustivel_2: Mapped[str | None] = mapped_column(Text, nullable=True)

    kit_application: Mapped["KitApplication | None"] = relationship(back_populates="catalog_record")


class KitFamily(Base):
    """Family level: grouping by all filter fields except combustivel_2."""

    __tablename__ = "kit_family"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    montadora: Mapped[str | None] = mapped_column(Text, nullable=True)
    ar_1: Mapped[str | None] = mapped_column(Text, nullable=True)
    ar_2: Mapped[str | None] = mapped_column(Text, nullable=True)
    lubrificante_1: Mapped[str | None] = mapped_column(Text, nullable=True)
    lubrificante_2: Mapped[str | None] = mapped_column(Text, nullable=True)
    combustivel_1: Mapped[str | None] = mapped_column(Text, nullable=True)

    family_key: Mapped[str] = mapped_column(String(1024), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    variants: Mapped[list["KitVariant"]] = relationship(back_populates="family", cascade="all, delete-orphan")


class KitVariant(Base):
    """Variant level: family + combustivel_2."""

    __tablename__ = "kit_variant"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kit_family_id: Mapped[int] = mapped_column(ForeignKey("kit_family.id", ondelete="CASCADE"), nullable=False)
    combustivel_2: Mapped[str | None] = mapped_column(Text, nullable=True)

    variant_key: Mapped[str] = mapped_column(String(1024), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    family: Mapped[KitFamily] = relationship(back_populates="variants")
    applications: Mapped[list["KitApplication"]] = relationship(back_populates="variant", cascade="all, delete-orphan")


class KitApplication(Base):
    """Link each original catalog row to one kit variant."""

    __tablename__ = "kit_application"
    __table_args__ = (
        UniqueConstraint("catalog_record_id", name="uq_kit_application_catalog_record"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    catalog_record_id: Mapped[int] = mapped_column(ForeignKey("catalog_record.id", ondelete="CASCADE"), nullable=False)
    kit_variant_id: Mapped[int] = mapped_column(ForeignKey("kit_variant.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    catalog_record: Mapped[CatalogRecord] = relationship(back_populates="kit_application")
    variant: Mapped[KitVariant] = relationship(back_populates="applications")


Index("ix_kit_family_family_key", KitFamily.family_key)
Index("ix_kit_variant_variant_key", KitVariant.variant_key)
Index("ix_kit_variant_kit_family_id", KitVariant.kit_family_id)
Index("ix_kit_application_catalog_record_id", KitApplication.catalog_record_id)
