from flask import Blueprint, jsonify

from db import get_db
from helpers import api_error, api_ok, primary_key_column, resolve_table

bp = Blueprint("reviews", __name__)


@bp.get("/reviews")
def list_reviews():
    table = resolve_table(["reviews", "product_reviews", "avaliacoes"])
    if not table:
        return jsonify(api_ok([], message="Tabela de reviews não encontrada; retornando vazio.")[0])
    rows = [dict(r) for r in get_db().execute(f"SELECT * FROM {table} ORDER BY ROWID DESC LIMIT 500").fetchall()]
    return jsonify(api_ok(rows)[0])


@bp.get("/reviews/<review_id>")
def get_review(review_id):
    table = resolve_table(["reviews", "product_reviews", "avaliacoes"])
    if not table:
        payload, status = api_error("Tabela de reviews não encontrada.", status=404)
        return jsonify(payload), status
    pk = primary_key_column(table)
    row = get_db().execute(f"SELECT * FROM {table} WHERE {pk} = ?", (review_id,)).fetchone()
    if not row:
        payload, status = api_error("Review não encontrada.", status=404)
        return jsonify(payload), status
    return jsonify(api_ok(dict(row))[0])
