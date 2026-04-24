import logging
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError

load_dotenv()
logger = logging.getLogger(__name__)


@dataclass
class DBConfig:
    sqlite_path: str = os.getenv("SQLITE_PATH", "tecfil_catalog.db")

    @property
    def sqlalchemy_url(self) -> str:
        return f"sqlite:///{self.sqlite_path}"


def ensure_sqlite_file_exists(config: DBConfig) -> None:
    db_file = Path(config.sqlite_path)
    if not db_file.exists():
        logger.info("Arquivo SQLite não existe. Criando: %s", db_file)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        db_file.touch()
    else:
        logger.info("Arquivo SQLite encontrado: %s", db_file)


def get_engine(config: DBConfig | None = None) -> Engine:
    config = config or DBConfig()
    ensure_sqlite_file_exists(config)

    engine = create_engine(
        config.sqlalchemy_url,
        pool_pre_ping=True,
        future=True,
    )

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Conexão com SQLite estabelecida")
    except OperationalError as exc:
        logger.exception("Falha de conexão com SQLite")
        raise RuntimeError("Não foi possível conectar ao banco SQLite") from exc

    return engine
