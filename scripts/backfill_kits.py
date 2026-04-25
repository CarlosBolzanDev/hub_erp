"""CLI routine to create tables and backfill kit merge data."""

from __future__ import annotations

import logging

from db import Base, SessionLocal, engine
from kit_merge import INCLUDE_MONTADORA_IN_FAMILY, backfill_kits

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")


def main() -> None:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        stats = backfill_kits(session, include_montadora=INCLUDE_MONTADORA_IN_FAMILY)

    logging.info("done backfill stats=%s", stats)


if __name__ == "__main__":
    main()
