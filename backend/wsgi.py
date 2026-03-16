"""WSGI entrypoint for production servers (e.g., gunicorn)."""

from app import app


if __name__ == "__main__":
    app.run()
