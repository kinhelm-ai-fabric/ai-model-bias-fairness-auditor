import csv
import io
import logging
import os

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app

from app.models.audit_store import (
    create_audit, get_audit, list_audits, delete_audit,
    update_audit_status, save_audit_results, get_audit_results,
    save_audit_report, get_audit_report,
)
from app.services.bias_metrics import parse_csv_data, compute_bias_metrics, summarize_metrics
from app.services.kindo_agent import generate_audit_report

logger = logging.getLogger(__name__)

audits_bp = Blueprint("audits", __name__)


@audits_bp.route("/audits")
def audit_list():
    try:
        audits = list_audits()
    except Exception as exc:
        logger.exception("audit_list: service error — %s", exc)
        return render_template("errors/500.html"), 500
    return render_template("pages/audit_list.html", audits=audits)


@audits_bp.route("/audits/new", methods=["GET", "POST"])
def audit_new():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        protected_attr = request.form.get("protected_attribute", "").strip()
        favorable_label = request.form.get("favorable_label", "1").strip()

        if not name or not protected_attr:
            flash("Audit name and protected attribute are required.", "danger")
            return render_template("pages/audit_new.html"), 400

        # Handle file upload
        file = request.files.get("dataset")
        dataset_filename = ""
        if file and file.filename:
            dataset_filename = file.filename
            upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], dataset_filename)
            file.save(upload_path)

        try:
            audit_id = create_audit(name, description, dataset_filename, protected_attr, favorable_label)
        except Exception as exc:
            logger.exception("audit_new: failed to create audit — %s", exc)
            flash("Failed to create audit.", "danger")
            return render_template("pages/audit_new.html"), 500

        # If dataset was uploaded, run the analysis immediately
        if dataset_filename:
            try:
                _run_audit_analysis(audit_id, dataset_filename, protected_attr, favorable_label)
                flash("Audit created and analysis completed.", "success")
            except Exception as exc:
                logger.exception("audit_new: analysis failed — %s", exc)
                flash("Audit created but analysis failed. You can retry from the audit page.", "warning")
        else:
            flash("Audit created. Upload a dataset to run analysis.", "success")

        return redirect(url_for("audits.audit_detail", audit_id=audit_id))

    return render_template("pages/audit_new.html")


@audits_bp.route("/audits/<int:audit_id>")
def audit_detail(audit_id):
    try:
        audit = get_audit(audit_id)
    except Exception as exc:
        logger.exception("audit_detail: service error — %s", exc)
        return render_template("errors/500.html"), 500

    if audit is None:
        flash("Audit not found.", "warning")
        return redirect(url_for("audits.audit_list"))

    try:
        results = get_audit_results(audit_id)
    except Exception as exc:
        logger.exception("audit_detail: failed to load results — %s", exc)
        results = []

    try:
        report = get_audit_report(audit_id)
    except Exception as exc:
        logger.exception("audit_detail: failed to load report — %s", exc)
        report = None

    return render_template("pages/audit_detail.html", audit=audit, results=results, report=report)


@audits_bp.route("/audits/<int:audit_id>/run", methods=["POST"])
def audit_run(audit_id):
    try:
        audit = get_audit(audit_id)
    except Exception as exc:
        logger.exception("audit_run: service error — %s", exc)
        flash("Failed to load audit.", "danger")
        return redirect(url_for("audits.audit_list"))

    if audit is None:
        flash("Audit not found.", "warning")
        return redirect(url_for("audits.audit_list"))

    if not audit["dataset_filename"]:
        flash("No dataset uploaded for this audit.", "warning")
        return redirect(url_for("audits.audit_detail", audit_id=audit_id))

    try:
        _run_audit_analysis(
            audit_id, audit["dataset_filename"],
            audit["protected_attribute"], audit["favorable_label"]
        )
        flash("Analysis completed successfully.", "success")
    except Exception as exc:
        logger.exception("audit_run: analysis failed — %s", exc)
        flash(f"Analysis failed: {exc}", "danger")

    return redirect(url_for("audits.audit_detail", audit_id=audit_id))


@audits_bp.route("/audits/<int:audit_id>/report", methods=["POST"])
def audit_generate_report(audit_id):
    try:
        audit = get_audit(audit_id)
    except Exception as exc:
        logger.exception("audit_generate_report: service error — %s", exc)
        flash("Failed to load audit.", "danger")
        return redirect(url_for("audits.audit_list"))

    if audit is None:
        flash("Audit not found.", "warning")
        return redirect(url_for("audits.audit_list"))

    try:
        results = get_audit_results(audit_id)
    except Exception as exc:
        logger.exception("audit_generate_report: failed to load results — %s", exc)
        flash("Failed to load audit results.", "danger")
        return redirect(url_for("audits.audit_detail", audit_id=audit_id))

    if not results:
        flash("Run the analysis first before generating a report.", "warning")
        return redirect(url_for("audits.audit_detail", audit_id=audit_id))

    try:
        metrics_summary = summarize_metrics(results)
        report_text = generate_audit_report(
            audit["name"], audit["description"],
            audit["protected_attribute"], metrics_summary
        )
        save_audit_report(audit_id, report_text)
        flash("AI audit report generated.", "success")
    except Exception as exc:
        logger.exception("audit_generate_report: report generation failed — %s", exc)
        flash(f"Report generation failed: {exc}", "danger")

    return redirect(url_for("audits.audit_detail", audit_id=audit_id))


@audits_bp.route("/audits/<int:audit_id>/delete", methods=["POST"])
def audit_delete(audit_id):
    try:
        delete_audit(audit_id)
        flash("Audit deleted.", "success")
    except Exception as exc:
        logger.exception("audit_delete: failed — %s", exc)
        flash("Failed to delete audit.", "danger")
    return redirect(url_for("audits.audit_list"))


def _run_audit_analysis(audit_id, dataset_filename, protected_attr, favorable_label):
    """Read the uploaded CSV and compute bias metrics."""
    upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], dataset_filename)
    if not os.path.exists(upload_path):
        raise FileNotFoundError(f"Dataset file not found: {dataset_filename}")

    with open(upload_path, "r", encoding="utf-8") as f:
        csv_text = f.read()

    rows = parse_csv_data(csv_text)
    if not rows:
        raise ValueError("Dataset is empty or could not be parsed")

    update_audit_status(audit_id, "running")

    try:
        results = compute_bias_metrics(rows, protected_attr, favorable=favorable_label)
        save_audit_results(audit_id, results)
        update_audit_status(audit_id, "completed")
    except Exception:
        update_audit_status(audit_id, "failed")
        raise
