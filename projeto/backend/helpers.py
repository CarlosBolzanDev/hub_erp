import json
from typing import Iterable

from db import get_db


def api_ok(data=None, message="ok", status=200, **meta):
    payload = {"success": True, "message": message, "data": data}
    if meta:
        payload["meta"] = meta
    return payload, status


def api_error(message, status=400, **meta):
    payload = {"success": False, "message": message, "data": None}
    if meta:
        payload["meta"] = meta
    return payload, status


def table_exists(table_name: str) -> bool:
    db = get_db()
    row = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name = ?", (table_name,)
    ).fetchone()
    return row is not None


def resolve_table(candidates: Iterable[str]):
    for name in candidates:
        if table_exists(name):
            return name
    return None


def table_columns(table_name: str):
    db = get_db()
    rows = db.execute(f"PRAGMA table_info({table_name})").fetchall()
    return [r["name"] for r in rows]


def primary_key_column(table_name: str):
    db = get_db()
    rows = db.execute(f"PRAGMA table_info({table_name})").fetchall()
    for r in rows:
        if r["pk"] == 1:
            return r["name"]
    cols = [r["name"] for r in rows]
    for fallback in ("id", "item_id", "product_id", "order_id", "sale_id"):
        if fallback in cols:
            return fallback
    return cols[0] if cols else None


def parse_jsonish(record: dict):
    parsed = {}
    for key, value in record.items():
        if isinstance(value, str) and value and value[0] in "[{":
            try:
                parsed[key] = json.loads(value)
            except json.JSONDecodeError:
                parsed[key] = value
        else:
            parsed[key] = value
    return parsed


def paginate_query(base_sql: str, params: list, page: int, per_page: int):
    offset = (page - 1) * per_page
    sql = f"{base_sql} LIMIT ? OFFSET ?"
    return sql, params + [per_page, offset]


def safe_insert(table: str, payload: dict, forbidden: set | None = None):
    forbidden = forbidden or set()
    cols = set(table_columns(table))
    clean = {k: v for k, v in payload.items() if k in cols and k not in forbidden}
    if not clean:
        return None, "Nenhum campo válido para inserir."
    fields = ", ".join(clean.keys())
    placeholders = ", ".join(["?"] * len(clean))
    values = list(clean.values())
    db = get_db()
    cursor = db.execute(
        f"INSERT INTO {table} ({fields}) VALUES ({placeholders})",
        values,
    )
    db.commit()
    return cursor.lastrowid, None


def safe_update(table: str, pk_col: str, pk_value, payload: dict):
    cols = set(table_columns(table))
    clean = {k: v for k, v in payload.items() if k in cols and k != pk_col}
    if not clean:
        return "Nenhum campo válido para atualizar."
    sets = ", ".join([f"{c} = ?" for c in clean])
    values = list(clean.values()) + [pk_value]
    db = get_db()
    db.execute(f"UPDATE {table} SET {sets} WHERE {pk_col} = ?", values)
    db.commit()
    return None
