import os

from dotenv import load_dotenv

# Load variables from .env into os.environ before Config reads them.
# This keeps secrets out of source code and lets settings differ per environment.
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # Flask uses this key to sign session cookies and other secure tokens.
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    # MySQL connection settings used by models/db.py.
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "civicfix")

    # Directory where uploaded issue images are stored.
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
    ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}
