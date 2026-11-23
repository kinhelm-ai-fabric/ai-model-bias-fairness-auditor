import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix


def create_app():
    app = Flask(__name__)

    # ── Security configuration ────────────────────────────────────────
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", os.urandom(32).hex())
    app.config["SESSION_COOKIE_NAME"] = "bias_auditor_session"
    app.config["SESSION_COOKIE_PATH"] = os.environ.get("SESSION_COOKIE_PATH", "/")
    app.config["SESSION_COOKIE_SECURE"] = os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # ── Data directory ────────────────────────────────────────────────
    data_dir = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "data"))
    os.makedirs(data_dir, exist_ok=True)
    app.config["DATA_DIR"] = data_dir
    app.config["UPLOAD_FOLDER"] = os.path.join(data_dir, "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB

    # ── Database ──────────────────────────────────────────────────────
    db_path = os.path.join(data_dir, "auditor.db")
    app.config["DATABASE_PATH"] = db_path

    # ── Logging ───────────────────────────────────────────────────────
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

    # ── ProxyFix ──────────────────────────────────────────────────────
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # ── Initialize database ──────────────────────────────────────────
    from app.models.database import init_db
    with app.app_context():
        init_db(app)

    # ── Register blueprints ──────────────────────────────────────────
    from app.routes.main import main_bp
    from app.routes.audits import audits_bp
    from app.routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(audits_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    return app
