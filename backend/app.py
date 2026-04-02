"""Flask application entry point."""

import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# Import route blueprints
from routes import analytics_bp, auth_bp, customers_bp, dashboard_bp

# Import services to initialize them
from services import ml_models
from config.database import ensure_admin_table


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def _parse_cors_origins():
    """Parse allowed origins for CORS.

    Defaults to "*" for quick deployment and can be restricted through
    CORS_ALLOWED_ORIGINS as a comma-separated list.
    """
    raw = os.getenv("CORS_ALLOWED_ORIGINS", "*")
    origins = [item.strip() for item in raw.split(",") if item.strip()]
    if "*" in origins:
        return "*"
    return origins


def create_app():
    app = Flask(__name__)

    env = os.getenv("FLASK_ENV", "development").lower()
    is_production = env == "production"

    jwt_secret = os.getenv("JWT_SECRET_KEY", "change-this-development-secret-before-production")
    if is_production and jwt_secret == "change-this-development-secret-before-production":
        raise RuntimeError("JWT_SECRET_KEY must be set in production.")

    app.config["JWT_SECRET_KEY"] = jwt_secret
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "28800"))
    app.config["JSON_SORT_KEYS"] = False

    JWTManager(app)
    CORS(
        app,
        resources={r"/api/*": {"origins": _parse_cors_origins()}},
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        supports_credentials=os.getenv("CORS_SUPPORTS_CREDENTIALS", "0") == "1",
    )

    require_db_on_startup = os.getenv("REQUIRE_DB_ON_STARTUP", "1") == "1"
    try:
        ensure_admin_table()
    except Exception as exc:
        if require_db_on_startup:
            raise
        print(f"⚠️ Database bootstrap skipped: {exc}")

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(dashboard_bp)

    return app


app = create_app()


# Run Flask application (development mode). Use Gunicorn with wsgi.py in production.
if __name__ == '__main__':
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    print(f"Starting Flask Server on http://{host}:{port}")
    print(f"CORS origins: {_parse_cors_origins()}")
    print(f"ML models loaded: {ml_models.is_loaded()}")
    app.run(host=host, port=port, debug=debug)