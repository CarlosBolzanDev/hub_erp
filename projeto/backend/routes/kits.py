from flask import Blueprint, jsonify, request

from db import get_db
from helpers import api_error, api_ok, primary_key_column, resolve_table, safe_insert, safe_update

bp = Blueprint("kits", __name__)


def _kits_table():
    return resolve_table(["kits", "product_kits", "bundles"])


@bp.get("/kits")
def list_kits():
    table = _kits_table()
    if not table:
        return jsonify(api_ok([], message="Tabela de kits não encontrada; retornando vazio.")[0])
    rows = [dict(r) for r in get_db().execute(f"SELECT * FROM {table} ORDER BY ROWID DESC LIMIT 500").fetchall()]
    return jsonify(api_ok(rows)[0])


@bp.post("/kits")
def create_kit():
    table = _kits_table()
    if not table:
        payload, status = api_error("Tabela de kits não encontrada.", status=404)
        return jsonify(payload), status
    pk = primary_key_column(table)
    new_id, error = safe_insert(table, request.get_json(silent=True) or {}, forbidden={pk})
    if error:
        payload, status = api_error(error, status=400)
        return jsonify(payload), status
    payload, status = api_ok({"id": new_id}, message="Kit criado.", status=201)
    return jsonify(payload), status


@bp.put("/kits/<kit_id>")
def update_kit(kit_id):
    table = _kits_table()
    if not table:
        payload, status = api_error("Tabela de kits não encontrada.", status=404)
        return jsonify(payload), status
    pk = primary_key_column(table)
    error = safe_update(table, pk, kit_id, request.get_json(silent=True) or {})
    if error:
        payload, status = api_error(error, status=400)
        return jsonify(payload), status
    return jsonify(api_ok({"id": kit_id}, message="Kit atualizado.")[0])


@bp.delete("/kits/<kit_id>")
def delete_kit(kit_id):
    table = _kits_table()
    if not table:
        payload, status = api_error("Tabela de kits não encontrada.", status=404)
        return jsonify(payload), status
    pk = primary_key_column(table)
    db = get_db()
    db.execute(f"DELETE FROM {table} WHERE {pk} = ?", (kit_id,))
    db.commit()
    return jsonify(api_ok({"id": kit_id}, message="Kit excluído.")[0])
