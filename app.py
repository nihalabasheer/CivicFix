from flask import Flask, redirect, send_from_directory, session, url_for

from config import Config
from routes.auth import auth_bp
from routes.department import department_bp
from routes.user import user_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config.setdefault("UPLOAD_FOLDER", Config.UPLOAD_FOLDER)

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(department_bp)

    @app.route("/uploads/<path:filename>")
    def serve_upload(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    @app.route("/")
    def index():
        if "user_id" in session:
            if session.get("role") == "dept":
                return redirect(url_for("department.dashboard"))
            return redirect(url_for("user.dashboard"))
        return redirect(url_for("auth.login"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
