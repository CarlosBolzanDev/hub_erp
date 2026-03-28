from flask import Blueprint, jsonify, request

from db import get_db
from helpers import api_ok, resolve_table

bp = Blueprint("settings", __name__)


@bp.get("/settings")
def get_settings():
    table = resolve_table(["settings", "app_settings", "config"])
    if not table:
        return jsonify(api_ok({}, message="Tabela de settings não encontrada; retornando objeto vazio.")[0])
    rows = [dict(r) for r in get_db().execute(f"SELECT * FROM {table}").fetchall()]
    return jsonify(api_ok(rows)[0])


@bp.put("/settings")
def update_settings():
    table = resolve_table(["settings", "app_settings", "config"])
    data = request.get_json(silent=True) or {}
    if not table:
        return jsonify(api_ok(data, message="Sem tabela de settings; alteração recebida sem persistência.")[0])

    cols = [r["name"] for r in get_db().execute(f"PRAGMA table_info({table})").fetchall()]
    key_col = next((c for c in ["key", "name", "setting_key"] if c in cols), None)
    val_col = next((c for c in ["value", "setting_value", "val"] if c in cols), None)

    if key_col and val_col:
        for key, value in data.items():
            get_db().execute(
                f"INSERT INTO {table} ({key_col}, {val_col}) VALUES (?, ?) "
                f"ON CONFLICT({key_col}) DO UPDATE SET {val_col}=excluded.{val_col}",
                (key, str(value)),
            )
        get_db().commit()
    return jsonify(api_ok(data, message="Configurações atualizadas.")[0])
