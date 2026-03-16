"""Authentication endpoints backed by MySQL admin credentials."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required
from werkzeug.security import check_password_hash

from config.database import get_admin_user


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    user = get_admin_user(username)
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