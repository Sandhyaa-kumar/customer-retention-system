"""Analytics routes derived from live customer predictions."""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from services.prediction_engine import get_analytics_payload, get_live_customer_predictions


analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/api/analytics', methods=['GET'])
@jwt_required()
def get_analytics():
    try:
        customers = get_live_customer_predictions()
        return jsonify(get_analytics_payload(customers))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
