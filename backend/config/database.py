"""Database configuration and lightweight bootstrap helpers."""

import os
from urllib.parse import parse_qs, quote_plus, urlparse

import pymysql
from dotenv import load_dotenv
from pymysql import MySQLError
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from werkzeug.security import generate_password_hash


BASE_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def _normalize_db_host(raw_host):
    """Normalize host values, including accidental URL/search-link input."""
    value = (raw_host or "").strip()
    if not value:
        return ""

    if value.startswith("http://") or value.startswith("https://"):
        parsed = urlparse(value)
        query_host = parse_qs(parsed.query).get("q", [""])[0].strip()
        if query_host:
            value = query_host
        elif parsed.hostname:
            value = parsed.hostname

    # Strip any protocol/path/port fragments so only hostname remains.
    value = value.split("//")[-1].split("/")[0].split(":")[0].strip()
    return value


def _resolve_ssl_ca_path(raw_path):
    value = (raw_path or "").strip()
    if not value:
        return os.path.join(BASE_DIR, "isrgrootx1.pem")
    if os.path.isabs(value):
        return os.path.normpath(value)
    return os.path.normpath(os.path.join(BASE_DIR, value))


def _get_db_config_from_env():
    database_url = os.getenv("DATABASE_URL", "").strip()
    if database_url:
        parsed = urlparse(database_url)
        query = parse_qs(parsed.query)
        ssl_ca = query.get("ssl_ca", [""])[0]
        return {
            "host": _normalize_db_host(parsed.hostname or ""),
            "user": parsed.username or "",
            "password": parsed.password or "",
            "database": (parsed.path or "").lstrip("/"),
            "port": int(parsed.port or 3306),
            "ssl_ca": _resolve_ssl_ca_path(ssl_ca),
            "database_url": database_url,
        }

    return {
        "host": _normalize_db_host(os.getenv("DB_HOST", "")),
        "user": os.getenv("DB_USER", ""),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", ""),
        "port": int(os.getenv("DB_PORT", "3306")),
        "ssl_ca": _resolve_ssl_ca_path(os.getenv("DB_SSL_CA", "isrgrootx1.pem")),
        "database_url": "",
    }


DB_CONFIG = _get_db_config_from_env()
SSL_CA_PATH = DB_CONFIG["ssl_ca"]

DEFAULT_ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

_ENGINE = None


def _build_sqlalchemy_url():
    if DB_CONFIG["database_url"]:
        return DB_CONFIG["database_url"]
    return (
        "mysql+pymysql://"
        f"{DB_CONFIG['user']}:{quote_plus(DB_CONFIG['password'])}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )


def get_cloud_engine() -> Engine:
    """Create/reuse the SQLAlchemy engine for TiDB Cloud."""
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = create_engine(
            _build_sqlalchemy_url(),
            pool_pre_ping=True,
            pool_recycle=1800,
            connect_args={
                "ssl_ca": SSL_CA_PATH,
                "connect_timeout": 10,
                "read_timeout": 30,
                "write_timeout": 30,
            },
        )
    return _ENGINE


def get_db_connection():
    """
    Establishes a direct PyMySQL connection with comprehensive error handling.
    Handles authentication errors gracefully.
    
    Returns:
        pymysql.connections.Connection: Active database connection
        
    Raises:
        Exception: If connection fails with detailed error message
    """
    try:
        conn = pymysql.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            port=DB_CONFIG["port"],
            ssl_ca=SSL_CA_PATH,
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=10,
            read_timeout=30,
            write_timeout=30,
            autocommit=False,
        )
        return conn
    except MySQLError as err:
        error_code = err.args[0] if err.args else None
        if error_code == 1045:  # Access Denied Error
            print(f"❌ MySQL Access Denied: Incorrect username or password.")
            raise Exception("Database authentication failed. Please check MySQL credentials.")
        elif error_code in (2003, 2005):  # Can't Connect / Unknown host
            print(f"❌ MySQL Connection Error: Cannot connect to database server.")
            raise Exception(
                "Database server is unreachable. "
                f"Verify TiDB host '{DB_CONFIG['host']}' and port {DB_CONFIG['port']}, "
                "and ensure your current public IP is allowlisted in TiDB Cloud."
            )
        elif error_code == 1049:  # Unknown Database
            print(f"❌ MySQL Error: Database '{DB_CONFIG['database']}' does not exist.")
            raise Exception(f"Database '{DB_CONFIG['database']}' not found.")
        else:
            print(f"❌ MySQL Error [{error_code}]: {err}")
            raise Exception(f"Database connection error: {err}")


def ensure_admin_table():
    """Create the admin authentication table and seed the default admin row."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
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
        if conn is not None:
            conn.close()


def get_admin_user(username):
    """Fetch a single admin user by username."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
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
        if conn is not None:
            conn.close()
