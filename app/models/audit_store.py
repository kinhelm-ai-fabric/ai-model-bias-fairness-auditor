import logging
from app.models.database import get_db

logger = logging.getLogger(__name__)


def create_audit(name, description, dataset_filename, protected_attribute, favorable_label="1"):
    """Create a new audit record."""
    db = get_db()
    cursor = db.execute(
        """INSERT INTO audits (name, description, dataset_filename, protected_attribute, favorable_label, status)
           VALUES (?, ?, ?, ?, ?, 'pending')""",
        (name, description, dataset_filename, protected_attribute, favorable_label),
    )
    db.commit()
    return cursor.lastrowid


def get_audit(audit_id):
    """Get a single audit by ID."""
    db = get_db()
    row = db.execute("SELECT * FROM audits WHERE id = ?", (audit_id,)).fetchone()
    return dict(row) if row else None


def list_audits():
    """List all audits ordered by most recent first."""
    db = get_db()
    rows = db.execute("SELECT * FROM audits ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]


def update_audit_status(audit_id, status):
    """Update the status of an audit."""
    db = get_db()
    db.execute(
        "UPDATE audits SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (status, audit_id),
    )
    db.commit()


def delete_audit(audit_id):
    """Delete an audit and its results."""
    db = get_db()
    db.execute("DELETE FROM audits WHERE id = ?", (audit_id,))
    db.commit()


def save_audit_results(audit_id, results):
    """Save a list of metric results for an audit.

    results: list of dicts with keys metric_name, metric_value, group_name, details
    """
    db = get_db()
    for r in results:
        db.execute(
            """INSERT INTO audit_results (audit_id, metric_name, metric_value, group_name, details)
               VALUES (?, ?, ?, ?, ?)""",
            (audit_id, r["metric_name"], r.get("metric_value"), r.get("group_name", ""), r.get("details", "")),
        )
    db.commit()


def get_audit_results(audit_id):
    """Get all metric results for an audit."""
    db = get_db()
    rows = db.execute(
        "SELECT * FROM audit_results WHERE audit_id = ? ORDER BY id", (audit_id,)
    ).fetchall()
    return [dict(r) for r in rows]


def save_audit_report(audit_id, report_text):
    """Save an AI-generated report for an audit."""
    db = get_db()
    # Remove any existing report for this audit before saving
    db.execute("DELETE FROM audit_reports WHERE audit_id = ?", (audit_id,))
    db.execute(
        "INSERT INTO audit_reports (audit_id, report_text) VALUES (?, ?)",
        (audit_id, report_text),
    )
    db.commit()


def get_audit_report(audit_id):
    """Get the AI-generated report for an audit."""
    db = get_db()
    row = db.execute(
        "SELECT * FROM audit_reports WHERE audit_id = ? ORDER BY created_at DESC LIMIT 1",
        (audit_id,),
    ).fetchone()
    return dict(row) if row else None
