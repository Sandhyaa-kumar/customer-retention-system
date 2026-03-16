"""Database configuration and lightweight bootstrap helpers."""

import os

import mysql.connector
from mysql.connector import Error as MySQLError
from werkzeug.security import generate_password_hash


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "sandhyaa"),
    "database": os.getenv("DB_NAME", "churn_db"),
    "auth_plugin": os.getenv("DB_AUTH_PLUGIN", "mysql_native_password"),
}

DEFAULT_ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")


def get_db_connection():
    """
    Establishes MySQL connection with comprehensive error handling.
    Handles authentication errors gracefully.
    
    Returns:
        mysql.connector.connection: Active database connection
        
    Raises:
        Exception: If connection fails with detailed error message
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except MySQLError as err:
        if err.errno == 1045:  # Access Denied Error
            print(f"❌ MySQL Access Denied: Incorrect username or password.")
            raise Exception("Database authentication failed. Please check MySQL credentials.")
        elif err.errno == 2003:  # Can't Connect
            print(f"❌ MySQL Connection Error: Cannot connect to database server.")
            raise Exception("Database server is not running or unreachable.")
        elif err.errno == 1049:  # Unknown Database
            print(f"❌ MySQL Error: Database 'churn_db' does not exist.")
            raise Exception("Database 'churn_db' not found. Please create it first.")
        else:
            print(f"❌ MySQL Error [{err.errno}]: {err}")
            raise Exception(f"Database connection error: {err.msg}")


def ensure_admin_table():
    """Create the admin authentication table and seed the default admin row."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS admin_users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL DEFAULT 'admin',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            "SELECT id FROM admin_users WHERE username = %s",
            (DEFAULT_ADMIN_USERNAME,),
        )
        admin_user = cursor.fetchone()

        if admin_user is None:
            cursor.execute(
                """
                INSERT INTO admin_users (username, password_hash, role)
                VALUES (%s, %s, 'admin')
                """,
                (DEFAULT_ADMIN_USERNAME, generate_password_hash(DEFAULT_ADMIN_PASSWORD)),
            )
            conn.commit()
            print("✅ Default admin account is available in MySQL.")
        else:
            conn.commit()
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


def get_admin_user(username):
    """Fetch a single admin user by username."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, username, password_hash, role, created_at, updated_at
            FROM admin_users
            WHERE username = %s
            """,
            (username,),
        )
        return cursor.fetchone()
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()
