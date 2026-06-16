from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from mysql.connector import Error as MySQLError
from werkzeug.security import check_password_hash, generate_password_hash

from models.db import DatabaseConnectionError, get_connection

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _redirect_for_role(role):
    """Send users to the dashboard that matches their role."""
    if role == "dept":
        return redirect(url_for("department.dashboard"))
    return redirect(url_for("user.dashboard"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not name or not email or not password:
        flash("All fields are required.", "danger")
        return render_template("register.html", name=name, email=email), 400

    if len(password) < 6:
        flash("Password must be at least 6 characters.", "danger")
        return render_template("register.html", name=name, email=email), 400

    password_hash = generate_password_hash(password)

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO users (name, email, password_hash, role, dept_id)
            VALUES (%s, %s, %s, 'normal', NULL)
            """,
            (name, email, password_hash),
        )
        conn.commit()

        user_id = cursor.lastrowid
        cursor.close()
        conn.close()

        session["user_id"] = user_id
        session["role"] = "normal"
        session["dept_id"] = None
        session["name"] = name

        flash("Registration successful!", "success")
        return _redirect_for_role("normal")

    except DatabaseConnectionError:
        flash("Database connection failed. Please try again.", "danger")
        return render_template("register.html", name=name, email=email), 500

    except MySQLError as exc:
        if exc.errno == 1062:
            flash("An account with this email already exists.", "danger")
            return render_template("register.html", name=name, email=email), 409

        flash("Registration failed. Please try again.", "danger")
        return render_template("register.html", name=name, email=email), 500


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not email or not password:
        flash("Email and password are required.", "danger")
        return render_template("login.html", email=email), 400

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT id, name, email, password_hash, role, dept_id FROM users WHERE email = %s",
            (email,),
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "danger")
            return render_template("login.html", email=email), 401

        session["user_id"] = user["id"]
        session["role"] = user["role"]
        session["dept_id"] = user["dept_id"]
        session["name"] = user["name"]

        flash("Login successful!", "success")
        return _redirect_for_role(user["role"])

    except DatabaseConnectionError:
        flash("Database connection failed. Please try again.", "danger")
        return render_template("login.html", email=email), 500


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
