import mysql.connector
from mysql.connector import Error, MySQLConnection

from config import Config


class DatabaseConnectionError(Exception):
    """Raised when a MySQL connection cannot be established."""


def get_connection() -> MySQLConnection:
    """
    Create and return a new MySQL database connection.

    Uses credentials from Config (loaded via python-dotenv from .env).
    Raises DatabaseConnectionError if the server is unreachable or auth fails.
    """
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
        )
        return connection
    except Error as exc:
        # Wrap mysql-connector errors so callers get a clear, app-level exception.
        raise DatabaseConnectionError(
            f"Failed to connect to MySQL at {Config.DB_HOST}/{Config.DB_NAME}: {exc}"
        ) from exc
