from flask import Blueprint, jsonify, request

from db import get_db
from helpers import (
    api_error,
    api_ok,
    paginate_query,
    parse_jsonish,
    primary_key_column,
    resolve_table,
    safe_insert,
    safe_update,
    table_columns,
)

bp = Blueprint("products", __name__)
PRODUCT_TABLES = ["products", "product", "items", "ml_products"]


def _product_table():
    return resolve_table(PRODUCT_TABLES)


@bp.get("/products")
def list_products():
    table = _product_table()
    if not table:
        return jsonify(api_ok([], message="Tabela de produtos não encontrada; retornando vazio.")[0])

    cols = table_columns(table)
    sql = f"SELECT * FROM {table} WHERE 1=1"
    params = []

    search = request.args.get("busca") or request.args.get("search")
    if search:
        text_cols = [c for c in cols if any(k in c.lower() for k in ["title", "name", "sku", "item", "desc"])][:3]
        if text_cols:
            clauses = [f"{c} LIKE ?" for c in text_cols]
            sql += f" AND ({' OR '.join(clauses)})"
            params.extend([f"%{search}%"] * len(text_cols))

    filters_map = {
        "status": ["status"],
        "condition": ["condition", "condicao"],
        "free_shipping": ["free_shipping", "frete_gratis"],
        "logistic": ["logistic_type", "logistica"],
    }
    for arg, candidates in filters_map.items():
        value = request.args.get(arg)
        if value is not None:
            col = next((c for c in candidates if c in cols), None)
            if col:
                sql += f" AND {col} = ?"
                params.append(value)

    page = max(1, int(request.args.get("page", 1)))
    per_page = min(200, max(1, int(request.args.get("per_page", 25))))

    count_sql = f"SELECT COUNT(*) as total FROM ({sql})"
    total = get_db().execute(count_sql, params).fetchone()["total"]
    paged_sql, paged_params = paginate_query(sql, params, page, per_page)
    rows = [parse_jsonish(dict(r)) for r in get_db().execute(paged_sql, paged_params).fetchall()]
    payload, status = api_ok(rows, total=total, page=page, per_page=per_page)
    return jsonify(payload), status


@bp.get("/products/<item_id>")
def get_product(item_id):
    table = _product_table()
    if not table:
        payload, status = api_error("Tabela de produtos não encontrada.", status=404)
        return jsonify(payload), status
    pk = primary_key_column(table)
    row = get_db().execute(f"SELECT * FROM {table} WHERE {pk} = ?", (item_id,)).fetchone()
    if not row:
        payload, status = api_error("Produto não encontrado.", status=404)
        return jsonify(payload), status
    payload, status = api_ok(parse_jsonish(dict(row)))
    return jsonify(payload), status


@bp.post("/products")
def create_product():
    table = _product_table()
    if not table:
        payload, status = api_error("Tabela de produtos não encontrada.", status=404)
        return jsonify(payload), status
    pk = primary_key_column(table)
    payload_data = request.get_json(silent=True) or {}
    new_id, error = safe_insert(table, payload_data, forbidden={pk})
    if error:
        payload, status = api_error(error, status=400)
        return jsonify(payload), status
    payload, status = api_ok({"id": new_id}, message="Produto criado.", status=201)
    return jsonify(payload), status


@bp.put("/products/<item_id>")
def update_product(item_id):
    table = _product_table()
    if not table:
        payload, status = api_error("Tabela de produtos não encontrada.", status=404)
        return jsonify(payload), status
    pk = primary_key_column(table)
    payload_data = request.get_json(silent=True) or {}
    error = safe_update(table, pk, item_id, payload_data)
    if error:
        payload, status = api_error(error, status=400)
        return jsonify(payload), status
    payload, status = api_ok({"id": item_id}, message="Produto atualizado.")
    return jsonify(payload), status


@bp.delete("/products/<item_id>")
def delete_product(item_id):
    table = _product_table()
    if not table:
        payload, status = api_error("Tabela de produtos não encontrada.", status=404)
        return jsonify(payload), status
    pk = primary_key_column(table)
    db = get_db()
    db.execute(f"DELETE FROM {table} WHERE {pk} = ?", (item_id,))
    db.commit()
    payload, status = api_ok({"id": item_id}, message="Produto excluído.")
    return jsonify(payload), status
