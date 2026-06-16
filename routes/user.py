import os
import uuid
from functools import wraps

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

from config import Config
from models.ai_classifier import detect_issue
from models.db import DatabaseConnectionError, get_connection


def _allowed_image(filename):
    """Return True if the file has an allowed image extension."""
    if "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[1].lower()
    return extension in Config.ALLOWED_IMAGE_EXTENSIONS


user_bp = Blueprint("user", __name__, url_prefix="/users")


def normal_user_required(view):
    """Allow access only to logged-in users with the normal role."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        if session.get("role") != "normal":
            return redirect(url_for("department.dashboard"))
        return view(*args, **kwargs)

    return wrapped


@user_bp.route("/dashboard")
@normal_user_required
def dashboard():
    return render_template("user/dashboard.html")


@user_bp.route("/report-issue", methods=["GET", "POST"])
@normal_user_required
def report_issue():
    if request.method == "GET":
        return render_template("user/report_issue.html")

    description = request.form.get("description", "").strip()
    location = request.form.get("location", "").strip()
    image = request.files.get("image")

    if not image or not image.filename:
        flash("An image is required.", "danger")
        return render_template("user/report_issue.html"), 400

    if not _allowed_image(image.filename):
        flash("Only JPG, JPEG, and PNG images are allowed.", "danger")
        return render_template("user/report_issue.html"), 400

    if not description or not location:
        flash("Description and location are required.", "danger")
        return render_template("user/report_issue.html"), 400

    extension = secure_filename(image.filename).rsplit(".", 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{extension}"
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, unique_filename)
    image.save(file_path)

    classification = detect_issue(file_path)
    relative_image_path = os.path.join("uploads", unique_filename).replace("\\", "/")

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO issues (user_id, image_path, description, location, category, dept_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'Pending')
            """,
            (
                session["user_id"],
                relative_image_path,
                description,
                location,
                classification["category"],
                classification["dept_id"],
            ),
        )
        conn.commit()
        cursor.close()
        conn.close()

        session.pop("pending_report", None)
        flash("Issue reported successfully!", "success")
        return redirect(url_for("user.my_issues"))

    except DatabaseConnectionError:
        flash("Database connection failed. Please try again.", "danger")
        return render_template("user/report_issue.html"), 500


@user_bp.route("/my-issues")
@normal_user_required
def my_issues():
    issues = []

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT issue_id, description, location, category, status, created_at
            FROM issues
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (session["user_id"],),
        )
        issues = cursor.fetchall()
        cursor.close()
        conn.close()

    except DatabaseConnectionError:
        flash("Could not load your issues. Please try again.", "danger")

    return render_template("user/my_issues.html", issues=issues)
