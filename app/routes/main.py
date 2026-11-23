import logging
from flask import Blueprint, render_template, session, request, redirect, url_for

logger = logging.getLogger(__name__)

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("pages/index.html")


@main_bp.route("/getting-started")
def getting_started():
    return render_template("pages/getting_started.html")


@main_bp.route("/health")
def health():
    return {"status": "ok"}, 200


@main_bp.route("/toggle-theme", methods=["POST"])
def toggle_theme():
    current = session.get("theme", "light")
    session["theme"] = "dark" if current == "light" else "light"
    return {"theme": session["theme"]}, 200
