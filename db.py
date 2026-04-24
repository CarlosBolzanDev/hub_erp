import logging
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError


load_dotenv()
logger = logging.getLogger(__name__)


@dataclass
class DBConfig:
    db_type: str = os.getenv("DB_TYPE", "mysql").lower()
    db_user: str = os.getenv("DB_USER", "root")
    db_password: str = os.getenv("DB_PASSWORD", "")
    db_host: str = os.getenv("DB_HOST", "127.0.0.1")
    db_port: int = int(os.getenv("DB_PORT", "3306"))
    db_name: str = os.getenv("DB_NAME", "tecfil_catalog")
    sqlite_path: str = os.getenv("SQLITE_PATH", "tecfil_catalog.db")

    @property
    def sqlalchemy_url(self) -> str:
        if self.db_type == "sqlite":
            return f"sqlite:///{self.sqlite_path}"
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
        )

    @property
    def server_url(self) -> str:
        if self.db_type == "sqlite":
            return self.sqlalchemy_url
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/?charset=utf8mb4"
        )


def ensure_database_exists(config: DBConfig) -> None:
    if config.db_type == "sqlite":
        logger.info("Usando SQLite em %s", config.sqlite_path)
        return

    logger.info("Verificando existência do banco '%s'", config.db_name)
    server_engine = create_engine(config.server_url, pool_pre_ping=True, future=True)
    try:
        with server_engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{config.db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            conn.commit()
        logger.info("Banco verificado/criado com sucesso")
    finally:
        server_engine.dispose()


def get_engine(config: DBConfig | None = None) -> Engine:
    config = config or DBConfig()
    ensure_database_exists(config)

    engine = create_engine(
        config.sqlalchemy_url,
        pool_pre_ping=True,
        pool_recycle=3600,
        future=True,
    )

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Conexão com banco estabelecida")
    except OperationalError as exc:
        logger.exception("Falha de conexão com banco")
        raise RuntimeError("Não foi possível conectar ao banco de dados") from exc

    return engine
