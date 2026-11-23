import sqlite3
import threading
import logging

from flask import g, current_app

logger = logging.getLogger(__name__)

_init_lock = threading.Lock()
_initialized = False

_SCHEMA = """
CREATE TABLE IF NOT EXISTS audits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    dataset_filename TEXT DEFAULT '',
    protected_attribute TEXT NOT NULL,
    favorable_label TEXT NOT NULL DEFAULT '1',
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    audit_id INTEGER NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL,
    group_name TEXT DEFAULT '',
    details TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (audit_id) REFERENCES audits(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS audit_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    audit_id INTEGER NOT NULL,
    report_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (audit_id) REFERENCES audits(id) ON DELETE CASCADE
);
"""


def get_db():
    """Get a database connection for the current request."""
    if "db" not in g:
        db_path = current_app.config["DATABASE_PATH"]
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db


def close_db(e=None):
    """Close database connection at end of request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """Initialize database schema. Idempotent — safe for multiple workers."""
    global _initialized
    if _initialized:
        return

    with _init_lock:
        if _initialized:
            return
        db_path = app.config["DATABASE_PATH"]
        try:
            conn = sqlite3.connect(db_path)
            conn.executescript(_SCHEMA)
            conn.close()
            logger.info("Database initialized at %s", db_path)
            _initialized = True
        except Exception as exc:
            logger.exception("Failed to initialize database: %s", exc)
            raise

    app.teardown_appcontext(close_db)
