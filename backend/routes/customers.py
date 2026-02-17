"""
Customers API Route
Handles customer data retrieval with ML predictions.
"""

from flask import Blueprint, jsonify
from mysql.connector import Error as MySQLError
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from config.database import get_db_connection
from services.ml_loader import ml_models


customers_bp = Blueprint('customers', __name__)


@customers_bp.route('/api/customers', methods=['GET'])
def get_customers():
    """
    Fetches customer data from MySQL, applies ML predictions, and returns JSON.
    Returns: Full customer details with ML predictions
    """
    try:
        # Validate ML models are loaded
        if not ml_models.is_loaded():
            return jsonify({"error": "ML models not loaded. Check server logs."}), 500

        model = ml_models.get_model()
        encoder = ml_models.get_encoder()
        feature_cols = ml_models.get_feature_columns()

        # Establish database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Fetch raw customer data
        query = "SELECT * FROM customers LIMIT 200"
        df = pd.read_sql(query, conn)
        conn.close()

        if df.empty:
            print("⚠️ WARNING: Database is connected but the 'customers' table is empty.")
            return jsonify([])

        # Verify required columns exist (case-sensitive check)
        missing_cols = [col for col in feature_cols if col not in df.columns]
        if missing_cols:
            print(f"❌ ERROR: Missing columns in database: {missing_cols}")
            print(f"📋 Available columns: {df.columns.tolist()}")
            return jsonify({
                "error": f"Database schema mismatch. Missing columns: {missing_cols}"
            }), 500

        # Prepare features for ML prediction
        X = df[feature_cols].copy()
        
        # Handle categorical encoding (subscription_type)
        if 'subscription_type' in X.columns:
            try:
                X['subscription_type'] = encoder.transform(X['subscription_type'])
            except ValueError as e:
                print(f"⚠️ Encoding Warning: Unknown subscription type found. {e}")
                # Handle unknown categories gracefully
                X['subscription_type'] = X['subscription_type'].apply(
                    lambda x: encoder.transform([x])[0] if x in encoder.classes_ else 0
                )
        
        # Generate churn probability predictions
        probabilities = model.predict_proba(X)[:, 1]
        df['risk_score'] = np.round(probabilities * 100, 1)
        
        # Map risk levels based on probability thresholds
        df['risk_level'] = df['risk_score'].apply(
            lambda x: 'High Risk' if x > 70 else ('Medium Risk' if x > 40 else 'Low Risk')
        )

        # Ensure health_score exists (if not in DB, calculate inverse of risk)
        if 'health_score' not in df.columns:
            df['health_score'] = np.round(100 - df['risk_score'], 1)

        # Convert last_login_days to actual date
        today = datetime.now()
        df['last_login'] = df['last_login_days'].apply(
            lambda days: (today - timedelta(days=int(days))).strftime('%Y-%m-%d')
        )
        
        # Determine status based on churn column
        df['status'] = df['churn'].apply(lambda x: 'Churned' if x == 1 else 'Active')
        
        # Determine activity status for badges
        df['activity_status'] = df.apply(
            lambda row: 'Inactive' if row['last_login_days'] > 30 else 
                       ('High Risk' if row['risk_score'] > 70 else 'Active'),
            axis=1
        )

        # Convert to JSON-friendly format with all necessary fields
        result = df[[
            'customer_id', 'customer_name', 'email_address', 'status', 
            'health_score', 'last_login', 'risk_level', 'risk_score',
            'activity_status', 'last_login_days', 'tenure_months',
            'login_frequency', 'support_ticket_count', 'unresolved_tickets'
        ]].to_dict(orient='records')
        
        print(f"✅ SUCCESS: Sending {len(result)} customers to Frontend.")
        return jsonify(result)

    except MySQLError as db_err:
        error_msg = f"Database error: {str(db_err)}"
        print(f"❌ MySQL ERROR: {error_msg}")
        return jsonify({"error": error_msg}), 500
    
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"❌ API ERROR: {error_msg}")
        print(f"Full traceback:\n{traceback.format_exc()}")
        return jsonify({"error": error_msg}), 500
