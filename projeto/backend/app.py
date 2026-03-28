from flask import Flask, jsonify
from flask_cors import CORS

from db import close_db, connect_db
from helpers import api_error, api_ok
from routes.descriptions import bp as descriptions_bp
from routes.kits import bp as kits_bp
from routes.products import bp as products_bp
from routes.reviews import bp as reviews_bp
from routes.sales import bp as sales_bp
from routes.settings import bp as settings_bp
from routes.shipping import bp as shipping_bp
from routes.sync import bp as sync_bp


def create_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(products_bp, url_prefix="/api")
    app.register_blueprint(descriptions_bp, url_prefix="/api")
    app.register_blueprint(reviews_bp, url_prefix="/api")
    app.register_blueprint(sales_bp, url_prefix="/api")
    app.register_blueprint(kits_bp, url_prefix="/api")
    app.register_blueprint(shipping_bp, url_prefix="/api")
    app.register_blueprint(sync_bp, url_prefix="/api")
    app.register_blueprint(settings_bp, url_prefix="/api")

    @app.get("/api/health")
    def health():
        try:
            conn = connect_db()
            conn.execute("SELECT 1").fetchone()
            conn.close()
            return jsonify(api_ok({"database": "connected"})[0])
        except FileNotFoundError as exc:
            payload, status = api_error(str(exc), status=500)
            return jsonify(payload), status
        except Exception as exc:  # noqa: BLE001
            payload, status = api_error(f"Erro ao abrir o banco: {exc}", status=500)
            return jsonify(payload), status

    @app.errorhandler(FileNotFoundError)
    def handle_missing_db(exc):
        payload, status = api_error(str(exc), status=500)
        return jsonify(payload), status

    @app.errorhandler(Exception)
    def handle_generic_error(exc):
        payload, status = api_error(f"Erro interno: {exc}", status=500)
        return jsonify(payload), status

    app.teardown_appcontext(close_db)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
