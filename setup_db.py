"""
Initialize the CivicFix MySQL database.

Creates the database, tables, default departments, and demo department accounts.
Safe to run multiple times — existing records are not duplicated.
"""

import os
import sys

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error
from werkzeug.security import generate_password_hash

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "civicfix")

DEFAULT_DEPARTMENTS = (
    (1, "Roads"),
    (2, "Waste Management"),
)

DEMO_ACCOUNTS = (
    {
        "name": "Roads Department",
        "email": "road@civicfix.com",
        "password": "road123",
        "dept_id": 1,
    },
    {
        "name": "Waste Management Department",
        "email": "waste@civicfix.com",
        "password": "waste123",
        "dept_id": 2,
    },
)

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(191) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('normal', 'dept') NOT NULL DEFAULT 'normal',
    dept_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_users_dept
        FOREIGN KEY (dept_id) REFERENCES departments (id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS issues (
    issue_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    image_path VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    dept_id INT NOT NULL,
    status ENUM('Pending', 'Assigned', 'In Progress', 'Resolved') NOT NULL DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_issues_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_issues_dept
        FOREIGN KEY (dept_id) REFERENCES departments (id)
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""


def connect_server():
    """Connect to MySQL without selecting a database."""
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def connect_database():
    """Connect to the CivicFix database."""
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )


def create_database(cursor):
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
        "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    print(f"Database '{DB_NAME}' is ready.")


def create_tables(cursor):
    for statement in CREATE_TABLES_SQL.strip().split(";"):
        statement = statement.strip()
        if statement:
            cursor.execute(statement)
    print("Tables created (departments, users, issues).")


def seed_departments(cursor):
    cursor.executemany(
        """
        INSERT INTO departments (id, name)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE name = VALUES(name)
        """,
        DEFAULT_DEPARTMENTS,
    )
    print("Default departments seeded (Roads, Waste Management).")


def seed_demo_accounts(cursor):
    for account in DEMO_ACCOUNTS:
        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (account["email"],),
        )
        if cursor.fetchone():
            print(f"Demo account already exists: {account['email']}")
            continue

        password_hash = generate_password_hash(account["password"])
        cursor.execute(
            """
            INSERT INTO users (name, email, password_hash, role, dept_id)
            VALUES (%s, %s, %s, 'dept', %s)
            """,
            (
                account["name"],
                account["email"],
                password_hash,
                account["dept_id"],
            ),
        )
        print(f"Demo account created: {account['email']}")


def main():
    try:
        conn = connect_server()
        cursor = conn.cursor()
        create_database(cursor)
        conn.commit()
        cursor.close()
        conn.close()

        conn = connect_database()
        cursor = conn.cursor()
        create_tables(cursor)
        seed_departments(cursor)
        seed_demo_accounts(cursor)
        conn.commit()
        cursor.close()
        conn.close()

        print("\nDatabase setup completed successfully!")
        print("You can now run: python app.py")

    except Error as exc:
        print(f"Database setup failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
