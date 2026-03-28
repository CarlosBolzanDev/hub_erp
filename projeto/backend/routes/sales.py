from flask import Blueprint, jsonify

from db import get_db
from helpers import api_error, api_ok, primary_key_column, resolve_table

bp = Blueprint("sales", __name__)


def _sales_table():
    return resolve_table(["sales", "orders", "pedidos"])


@bp.get("/sales")
def list_sales():
    table = _sales_table()
    if not table:
        return jsonify(api_ok([], message="Tabela de vendas não encontrada; retornando vazio.")[0])
    rows = [dict(r) for r in get_db().execute(f"SELECT * FROM {table} ORDER BY ROWID DESC LIMIT 500").fetchall()]
    return jsonify(api_ok(rows)[0])


@bp.get("/sales/<sale_id>")
def get_sale(sale_id):
    table = _sales_table()
    if not table:
        payload, status = api_error("Tabela de vendas não encontrada.", status=404)
        return jsonify(payload), status
    pk = primary_key_column(table)
    row = get_db().execute(f"SELECT * FROM {table} WHERE {pk} = ?", (sale_id,)).fetchone()
    if not row:
        payload, status = api_error("Venda não encontrada.", status=404)
        return jsonify(payload), status
    return jsonify(api_ok(dict(row))[0])


@bp.get("/sales/<sale_id>/items")
def get_sale_items(sale_id):
    table = resolve_table(["sale_items", "order_items", "items_sales"])
    if not table:
        return jsonify(api_ok([], message="Tabela de itens de venda não encontrada; retornando vazio.")[0])
    cols = [r["name"] for r in get_db().execute(f"PRAGMA table_info({table})").fetchall()]
    sale_fk = next((c for c in ["sale_id", "order_id", "pedido_id"] if c in cols), None)
    if not sale_fk:
        return jsonify(api_ok([], message="Campo de relação de itens não encontrado.")[0])
    rows = [dict(r) for r in get_db().execute(f"SELECT * FROM {table} WHERE {sale_fk} = ?", (sale_id,)).fetchall()]
    return jsonify(api_ok(rows)[0])
