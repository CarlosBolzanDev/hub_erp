from datetime import datetime

from flask import Blueprint, jsonify

from db import get_db
from helpers import api_ok, resolve_table

bp = Blueprint("sync", __name__)


@bp.get("/sync/logs")
def list_sync_logs():
    table = resolve_table(["sync_logs", "logs_sync", "sync_history"])
    if not table:
        return jsonify(api_ok([], message="Tabela de logs de sync não encontrada; retornando vazio.")[0])
    rows = [dict(r) for r in get_db().execute(f"SELECT * FROM {table} ORDER BY ROWID DESC LIMIT 500").fetchall()]
    return jsonify(api_ok(rows)[0])


@bp.post("/sync/run")
def run_sync():
    table = resolve_table(["sync_logs", "logs_sync", "sync_history"])
    if table:
        cols = [r["name"] for r in get_db().execute(f"PRAGMA table_info({table})").fetchall()]
        if {"action", "created_at"}.issubset(cols):
            get_db().execute(
                f"INSERT INTO {table} (action, created_at) VALUES (?, ?)",
                ("manual_sync", datetime.utcnow().isoformat()),
            )
            get_db().commit()
    return jsonify(api_ok({"started": True, "at": datetime.utcnow().isoformat()}, message="Sincronização disparada.")[0])
