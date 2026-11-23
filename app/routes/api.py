import logging
from flask import Blueprint, jsonify, request

from app.models.audit_store import list_audits, get_audit, get_audit_results, get_audit_report

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__)


@api_bp.route("/audits")
def api_list_audits():
    try:
        audits = list_audits()
    except Exception as exc:
        logger.exception("api_list_audits: error — %s", exc)
        return jsonify({"error": "Failed to load audits", "detail": str(exc)}), 500
    return jsonify({"audits": audits})


@api_bp.route("/audits/<int:audit_id>")
def api_get_audit(audit_id):
    try:
        audit = get_audit(audit_id)
    except Exception as exc:
        logger.exception("api_get_audit: error — %s", exc)
        return jsonify({"error": "Failed to load audit", "detail": str(exc)}), 500

    if audit is None:
        return jsonify({"error": "Audit not found"}), 404

    try:
        results = get_audit_results(audit_id)
    except Exception as exc:
        logger.exception("api_get_audit: results error — %s", exc)
        results = []

    try:
        report = get_audit_report(audit_id)
    except Exception as exc:
        logger.exception("api_get_audit: report error — %s", exc)
        report = None

    return jsonify({
        "audit": audit,
        "results": results,
        "report": report,
    })


@api_bp.route("/health")
def api_health():
    return jsonify({"status": "ok"})
