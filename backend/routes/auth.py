"""Authentication endpoints backed by MySQL admin credentials."""

import os

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required
from werkzeug.security import check_password_hash

from config.database import get_admin_user


auth_bp = Blueprint("auth", __name__)


def _allow_local_fallback_auth():
    return os.getenv("ALLOW_LOCAL_FALLBACK_AUTH", "0") == "1"


def _local_fallback_user(username, password):
    if not _allow_local_fallback_auth():
        return None

    fallback_username = os.getenv("ADMIN_USERNAME", "").strip()
    fallback_password = os.getenv("ADMIN_PASSWORD", "")

    if not fallback_username or not fallback_password:
        return None

    if username == fallback_username and password == fallback_password:
        return {"username": fallback_username, "role": "admin"}

    return None


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    try:
        user = get_admin_user(username)
    except Exception as exc:
        print(f"❌ Login DB error: {exc}")

        fallback_user = _local_fallback_user(username, password)
        if fallback_user is not None:
            access_token = create_access_token(
                identity=fallback_user["username"],
                additional_claims={"role": fallback_user["role"]},
            )
            return jsonify(
                {
                    "token": access_token,
                    "user": fallback_user,
                }
            )

        return (
            jsonify(
                {
                    "error": (
                        "Authentication service is temporarily unavailable. "
                        "Verify backend .env database settings."
                    )
                }
            ),
            503,
        )

    if user is None or user.get("role") != "admin":
        return jsonify({"error": "Invalid credentials."}), 401

    if not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid credentials."}), 401

    access_token = create_access_token(
        identity=user["username"],
        additional_claims={"role": user["role"]},
    )

    return jsonify(
        {
            "token": access_token,
            "user": {
                "username": user["username"],
                "role": user["role"],
            },
        }
    )


@auth_bp.route("/api/auth/me", methods=["GET"])
@jwt_required()
def me():
    claims = get_jwt()
    return jsonify(
        {
            "user": {
                "username": get_jwt_identity(),
                "role": claims.get("role", "admin"),
            }
        }
    )