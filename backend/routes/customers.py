"""Customer API routes powered by live model inference."""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from services.prediction_engine import get_live_customer_predictions

customers_bp = Blueprint('customers', __name__)


@customers_bp.route('/api/customers', methods=['GET'])
@jwt_required()
def get_customers():
    try:
        customers = get_live_customer_predictions()
        return jsonify(customers)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@customers_bp.route('/api/customers/<customer_id>', methods=['GET'])
@jwt_required()
def get_customer_detail(customer_id):
    try:
        customers = get_live_customer_predictions()
        customer = next((item for item in customers if str(item.get('customer_id')) == str(customer_id)), None)
        if customer is None:
            return jsonify({"error": "Customer not found."}), 404
        return jsonify(customer)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
