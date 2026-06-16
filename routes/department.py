from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models.db import DatabaseConnectionError, get_connection

department_bp = Blueprint("department", __name__, url_prefix="/departments")

DEPT_NAMES = {
    1: "Road Department",
    2: "Waste Management Department",
}

ALLOWED_STATUSES = ("Pending", "Assigned", "In Progress", "Resolved")


def dept_user_required(view):
    """Allow access only to logged-in users with the dept role."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        if session.get("role") != "dept":
            return redirect(url_for("user.dashboard"))
        return view(*args, **kwargs)

    return wrapped


@department_bp.route("/dashboard")
@dept_user_required
def dashboard():
    issues = []
    dept_id = session.get("dept_id")
    dept_name = DEPT_NAMES.get(dept_id, "Department")

    if dept_id is not None:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT issue_id, image_path, description, location, category, status, created_at
                FROM issues
                WHERE dept_id = %s
                ORDER BY created_at DESC
                """,
                (dept_id,),
            )
            issues = cursor.fetchall()
            cursor.close()
            conn.close()

        except DatabaseConnectionError:
            flash("Could not load department issues. Please try again.", "danger")

    return render_template(
        "department_dashboard.html",
        issues=issues,
        dept_name=dept_name,
        statuses=ALLOWED_STATUSES,
    )


@department_bp.route("/issues/<int:issue_id>/status", methods=["POST"])
@dept_user_required
def update_issue_status(issue_id):
    status = request.form.get("status", "").strip()
    dept_id = session.get("dept_id")

    if status not in ALLOWED_STATUSES:
        flash("Invalid status selected.", "danger")
        return redirect(url_for("department.dashboard"))

    if dept_id is None:
        flash("Your account is not linked to a department.", "danger")
        return redirect(url_for("department.dashboard"))

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE issues
            SET status = %s
            WHERE issue_id = %s AND dept_id = %s
            """,
            (status, issue_id, dept_id),
        )
        conn.commit()

        if cursor.rowcount == 0:
            flash("Issue not found or not assigned to your department.", "danger")
        else:
            flash("Issue status updated successfully!", "success")

        cursor.close()
        conn.close()

    except DatabaseConnectionError:
        flash("Could not update issue status. Please try again.", "danger")

    return redirect(url_for("department.dashboard"))
