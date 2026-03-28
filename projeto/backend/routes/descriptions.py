from flask import Blueprint, jsonify, request

from db import get_db
from helpers import api_error, api_ok, primary_key_column, resolve_table, safe_update

bp = Blueprint("descriptions", __name__)


@bp.get("/descriptions")
def list_descriptions():
    table = resolve_table(["descriptions", "product_descriptions", "items"])
    if not table:
        return jsonify(api_ok([], message="Tabela de descrições não encontrada; retornando vazio.")[0])
    rows = [dict(r) for r in get_db().execute(f"SELECT * FROM {table} LIMIT 200").fetchall()]
    return jsonify(api_ok(rows)[0])


@bp.get("/descriptions/<item_id>")
def get_description(item_id):
    table = resolve_table(["descriptions", "product_descriptions", "items"])
    if not table:
        payload, status = api_error("Tabela de descrições não encontrada.", status=404)
        return jsonify(payload), status
    pk = primary_key_column(table)
    row = get_db().execute(f"SELECT * FROM {table} WHERE {pk} = ?", (item_id,)).fetchone()
    if not row:
        payload, status = api_error("Descrição não encontrada.", status=404)
        return jsonify(payload), status
    return jsonify(api_ok(dict(row))[0])


@bp.put("/descriptions/<item_id>")
def update_description(item_id):
    table = resolve_table(["descriptions", "product_descriptions", "items"])
    if not table:
        payload, status = api_error("Tabela de descrições não encontrada.", status=404)
        return jsonify(payload), status
    pk = primary_key_column(table)
    data = request.get_json(silent=True) or {}
    error = safe_update(table, pk, item_id, data)
    if error:
        payload, status = api_error(error, status=400)
        return jsonify(payload), status
    return jsonify(api_ok({"id": item_id}, message="Descrição atualizada.")[0])
