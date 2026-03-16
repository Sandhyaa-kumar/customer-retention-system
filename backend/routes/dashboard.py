"""Dashboard routes driven by live churn inference."""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from services.ml_loader import ml_models
from services.prediction_engine import get_dashboard_payload, get_live_customer_predictions


dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/api/dashboard-stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    try:
        customers = get_live_customer_predictions()
        return jsonify(get_dashboard_payload(customers))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify API is running."""
    return jsonify({
        "status": "healthy",
        "models_loaded": ml_models.is_loaded(),
        "message": "Flask API is running"
    })
