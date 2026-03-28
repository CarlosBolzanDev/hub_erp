import os
import sqlite3
from flask import g

DEFAULT_DB_PATH = r"C:\Users\ADM\Desktop\Invex-web\backend_bd\ml_backend.db"


def get_db_path() -> str:
    return os.getenv("ML_BACKEND_DB_PATH", DEFAULT_DB_PATH)


def connect_db() -> sqlite3.Connection:
    db_path = get_db_path()
    if not os.path.exists(db_path):
        raise FileNotFoundError(
            f"Arquivo SQLite não encontrado em: {db_path}. "
            "Defina ML_BACKEND_DB_PATH para um caminho válido."
        )
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_db() -> sqlite3.Connection:
    if "db_conn" not in g:
        g.db_conn = connect_db()
    return g.db_conn


def close_db(_error=None) -> None:
    conn = g.pop("db_conn", None)
    if conn is not None:
        conn.close()


def rows_to_dicts(rows):
    return [dict(row) for row in rows]
