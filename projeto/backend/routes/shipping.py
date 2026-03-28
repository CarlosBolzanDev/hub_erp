from flask import Blueprint, jsonify

from db import get_db
from helpers import api_ok, resolve_table

bp = Blueprint("shipping", __name__)


@bp.get("/shipping-quotes")
def list_shipping_quotes():
    table = resolve_table(["shipping_quotes", "freight_quotes", "shipping"])
    if not table:
        return jsonify(api_ok([], message="Tabela de frete não encontrada; retornando vazio.")[0])
    rows = [dict(r) for r in get_db().execute(f"SELECT * FROM {table} ORDER BY ROWID DESC LIMIT 500").fetchall()]
    return jsonify(api_ok(rows)[0])
