"""Kit merge rules, normalization, ingestion and read queries.

Business rule summary:
- Family key groups by ar_1, ar_2, lubrificante_1, lubrificante_2, combustivel_1
  and optionally montadora (configurable).
- Variant key is always family key + combustivel_2.
- Metadata fields (modelo, motor, ano_de, ano_ate, etc.) remain only in
  catalog_record and do not block kit grouping.
"""

from __future__ import annotations

import logging
import os
import unicodedata
from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import CatalogRecord, KitApplication, KitFamily, KitVariant

logger = logging.getLogger(__name__)


INCLUDE_MONTADORA_IN_FAMILY = os.getenv("INCLUDE_MONTADORA_IN_FAMILY", "true").strip().lower() in {
    "1",
    "true",
    "yes",
    "y",
    "on",
}


def normalize_key_part(value: object) -> str:
    """Normalize key parts to guarantee deterministic grouping.

    Rules:
    - None -> ""
    - trim extra spaces
    - remove accents
    - uppercase
    - normalize separators to single spaces
    """

    if value is None:
        return ""

    text = str(value)
    text = " ".join(text.split())
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("|", "/")
    return text.upper().strip()


def build_family_key(record: CatalogRecord, include_montadora: bool = INCLUDE_MONTADORA_IN_FAMILY) -> str:
    """Build family key from normalized fields.

    If `include_montadora` is false, merging can happen across manufacturers
    when filter fields are identical.
    """

    parts: list[str] = []
    if include_montadora:
        parts.append(normalize_key_part(record.montadora))

    parts.extend(
        [
            normalize_key_part(record.ar_1),
            normalize_key_part(record.ar_2),
            normalize_key_part(record.lubrificante_1),
            normalize_key_part(record.lubrificante_2),
            normalize_key_part(record.combustivel_1),
        ]
    )
    return "|".join(parts)


def build_variant_key(record: CatalogRecord, include_montadora: bool = INCLUDE_MONTADORA_IN_FAMILY) -> str:
    """Build variant key as family key + combustivel_2."""

    family_key = build_family_key(record=record, include_montadora=include_montadora)
    return f"{family_key}|{normalize_key_part(record.combustivel_2)}"


def get_or_create_family(session: Session, record: CatalogRecord, family_key: str) -> tuple[KitFamily, bool]:
    family = session.execute(select(KitFamily).where(KitFamily.family_key == family_key)).scalar_one_or_none()
    if family:
        return family, False

    family = KitFamily(
        montadora=record.montadora if INCLUDE_MONTADORA_IN_FAMILY else None,
        ar_1=record.ar_1,
        ar_2=record.ar_2,
        lubrificante_1=record.lubrificante_1,
        lubrificante_2=record.lubrificante_2,
        combustivel_1=record.combustivel_1,
        family_key=family_key,
    )
    session.add(family)
    session.flush()
    return family, True


def get_or_create_variant(session: Session, family: KitFamily, record: CatalogRecord, variant_key: str) -> tuple[KitVariant, bool]:
    variant = session.execute(select(KitVariant).where(KitVariant.variant_key == variant_key)).scalar_one_or_none()
    if variant:
        return variant, False

    variant = KitVariant(kit_family_id=family.id, combustivel_2=record.combustivel_2, variant_key=variant_key)
    session.add(variant)
    session.flush()
    return variant, True


def link_catalog_to_variant(session: Session, catalog_record_id: int, variant_id: int) -> tuple[KitApplication, bool]:
    mapping = session.execute(
        select(KitApplication).where(KitApplication.catalog_record_id == catalog_record_id)
    ).scalar_one_or_none()

    if mapping:
        if mapping.kit_variant_id != variant_id:
            mapping.kit_variant_id = variant_id
            logger.info("updated_link catalog_record_id=%s variant_id=%s", catalog_record_id, variant_id)
        return mapping, False

    mapping = KitApplication(catalog_record_id=catalog_record_id, kit_variant_id=variant_id)
    session.add(mapping)
    session.flush()
    return mapping, True


def backfill_kits(session: Session, include_montadora: bool = INCLUDE_MONTADORA_IN_FAMILY) -> dict[str, int]:
    """Idempotent backfill from catalog_record to kit_* tables."""

    stats = {
        "families_created": 0,
        "families_reused": 0,
        "variants_created": 0,
        "variants_reused": 0,
        "links_created": 0,
        "links_reused": 0,
    }

    records = session.execute(select(CatalogRecord)).scalars().all()
    logger.info("processing catalog records total=%s", len(records))

    for record in records:
        family_key = build_family_key(record, include_montadora=include_montadora)
        variant_key = build_variant_key(record, include_montadora=include_montadora)

        family, family_created = get_or_create_family(session, record, family_key)
        stats["families_created" if family_created else "families_reused"] += 1

        variant, variant_created = get_or_create_variant(session, family, record, variant_key)
        stats["variants_created" if variant_created else "variants_reused"] += 1

        _, link_created = link_catalog_to_variant(session, catalog_record_id=record.id, variant_id=variant.id)
        stats["links_created" if link_created else "links_reused"] += 1

    session.commit()
    logger.info("backfill completed stats=%s", stats)
    return stats


def list_kit_families(session: Session) -> list[KitFamily]:
    return session.execute(select(KitFamily).order_by(KitFamily.id)).scalars().all()


def list_variants_by_family(session: Session, kit_family_id: int) -> list[KitVariant]:
    return session.execute(select(KitVariant).where(KitVariant.kit_family_id == kit_family_id).order_by(KitVariant.id)).scalars().all()


def list_vehicles_by_variant(session: Session, kit_variant_id: int) -> list[CatalogRecord]:
    rows: Iterable[CatalogRecord] = session.execute(
        select(CatalogRecord)
        .join(KitApplication, KitApplication.catalog_record_id == CatalogRecord.id)
        .where(KitApplication.kit_variant_id == kit_variant_id)
        .order_by(CatalogRecord.montadora, CatalogRecord.modelo)
    ).scalars()
    return list(rows)


def list_montadora_modelo_by_variant(session: Session, kit_variant_id: int) -> list[tuple[str | None, str | None]]:
    rows = session.execute(
        select(CatalogRecord.montadora, CatalogRecord.modelo)
        .join(KitApplication, KitApplication.catalog_record_id == CatalogRecord.id)
        .where(KitApplication.kit_variant_id == kit_variant_id)
        .distinct()
        .order_by(CatalogRecord.montadora, CatalogRecord.modelo)
    ).all()
    return [(row[0], row[1]) for row in rows]


def kit_variant_application_report(session: Session) -> list[dict[str, object]]:
    """Return report rows equivalent to a SQL view payload."""

    rows = session.execute(
        select(
            CatalogRecord.montadora,
            CatalogRecord.modelo,
            CatalogRecord.ano_de,
            CatalogRecord.ano_ate,
            CatalogRecord.motor,
            CatalogRecord.ar_1,
            CatalogRecord.ar_2,
            CatalogRecord.lubrificante_1,
            CatalogRecord.lubrificante_2,
            CatalogRecord.combustivel_1,
            CatalogRecord.combustivel_2,
            KitFamily.id.label("kit_family_id"),
            KitVariant.id.label("kit_variant_id"),
        )
        .join(KitApplication, KitApplication.catalog_record_id == CatalogRecord.id)
        .join(KitVariant, KitVariant.id == KitApplication.kit_variant_id)
        .join(KitFamily, KitFamily.id == KitVariant.kit_family_id)
        .order_by(KitFamily.id, KitVariant.id, CatalogRecord.montadora, CatalogRecord.modelo)
    ).mappings()
    return [dict(row) for row in rows]
