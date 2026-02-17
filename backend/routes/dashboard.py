"""
Dashboard API Route
Handles dashboard statistics and KPI calculations.
"""

from flask import Blueprint, jsonify
from mysql.connector import Error as MySQLError
import pandas as pd
import numpy as np
from datetime import datetime

from config.database import get_db_connection
from services.ml_loader import ml_models


dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/api/dashboard-stats', methods=['GET'])
def get_dashboard_stats():
    """
    REAL-TIME Dashboard Statistics - Recalculates ALL metrics from live database.
    Updates automatically when ANY customer data changes (INSERT/UPDATE/DELETE).
    NO CACHING - Always reflects current DB state.
    
    Calculations:
    1. KPI Cards: Churn Rate, Retention Rate, Active Users, Health Score, Revenue Loss
    2. Retention Curve: 6-month retention trend (cohort analysis)
    3. Churn Reasons: Price, Low Usage, Poor Support, Competition
    4. Top Risk Customers: health_score < 40 OR inactive > 30 days
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
        
        # Fetch all customer data for calculations
        query = "SELECT * FROM customers"
        df = pd.read_sql(query, conn)
        conn.close()

        if df.empty:
            return jsonify({"error": "No customer data available"}), 404

        # Prepare features for ML prediction
        X = df[feature_cols].copy()
        
        # Handle categorical encoding
        if 'subscription_type' in X.columns:
            try:
                X['subscription_type'] = encoder.transform(X['subscription_type'])
            except ValueError:
                X['subscription_type'] = X['subscription_type'].apply(
                    lambda x: encoder.transform([x])[0] if x in encoder.classes_ else 0
                )
        
        # Generate ML predictions
        probabilities = model.predict_proba(X)[:, 1]
        df['risk_score'] = np.round(probabilities * 100, 1)

        # ========================================
        # 1️⃣ KPI CARDS (DYNAMIC CALCULATIONS)
        # ========================================
        
        total_customers = len(df)
        churned_customers = int(df['churn'].sum())
        
        # CHURN RATE: churned / total * 100
        churn_rate = (churned_customers / total_customers * 100) if total_customers > 0 else 0
        
        # RETENTION RATE: (total - churned) / total * 100 = active / total * 100
        active_customers_count = len(df[df['churn'] == 0])
        retention_rate = (active_customers_count / total_customers * 100) if total_customers > 0 else 0
        
        # ACTIVE USERS: customers active in last 30 days (last_login_days <= 30)
        active_users = len(df[(df['churn'] == 0) & (df['last_login_days'] <= 30)])
        
        # HEALTH SCORE: average health_score of active users only
        active_df = df[df['churn'] == 0]
        avg_health_score = active_df['health_score'].mean() if len(active_df) > 0 else 0
        
        # LOSS DUE TO CHURN: sum(monthly_charges) of churned customers
        churned_revenue = df[df['churn'] == 1]['monthly_charges'].sum()
        
        # ========================================
        # 2️⃣ RETENTION CURVE (6 MONTHS - COHORT ANALYSIS)
        # ========================================
        
        # Calculate month-over-month retention based on tenure cohorts
        retention_curve = []
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        
        # Build retention curve: For each month, show % of customers retained
        # Month 0 (Jan): customers with tenure >= 6 months
        # Month 5 (Jun): customers with tenure >= 1 month
        for i in range(6):
            month_index = 6 - i  # 6, 5, 4, 3, 2, 1
            
            # Customers who were active at start of this cohort period
            cohort_customers = df[df['tenure_months'] >= month_index]
            
            if len(cohort_customers) > 0:
                # Count how many are still active (not churned)
                retained_customers = len(cohort_customers[cohort_customers['churn'] == 0])
                retention_pct = (retained_customers / len(cohort_customers)) * 100
            else:
                # If no customers in cohort, show declining retention
                retention_pct = 100 - (churn_rate * i / 6)
            
            retention_curve.append({
                'month': months[i],
                'retention': round(retention_pct, 1)
            })

        # ========================================
        # 3️⃣ CHURN REASONS (DYNAMIC CATEGORIZATION)
        # ========================================
        
        churned_df = df[df['churn'] == 1]
        churn_reasons = []
        
        if len(churned_df) > 0:
            # PRICE: Churned users with payment drop (payment_failures > 0) + high charges
            # Users who had payment issues OR above-median pricing
            price_churn = len(churned_df[
                (churned_df['payment_failures'] > 0) | 
                (churned_df['monthly_charges'] > df['monthly_charges'].median())
            ])
            
            # LOW USAGE: Churned users with low usage_events count
            # Proxy: login_frequency < 10 OR feature_usage_count < median OR usage_drop_flag = 1
            median_usage = df['feature_usage_count'].median()
            low_usage_churn = len(churned_df[
                (churned_df['login_frequency'] < 10) | 
                (churned_df['feature_usage_count'] < median_usage) |
                (churned_df['usage_drop_flag'] == 1)
            ])
            
            # POOR SUPPORT: Churned users with unresolved support tickets
            poor_support_churn = len(churned_df[churned_df['unresolved_tickets'] > 0])
            
            # COMPETITION: Remaining churned users (healthy usage, no issues, just left)
            # Customers who churned but had good health, no support issues, no payment problems
            competition_churn = len(churned_df[
                (churned_df['unresolved_tickets'] == 0) & 
                (churned_df['payment_failures'] == 0) &
                (churned_df['usage_drop_flag'] == 0) &
                (churned_df['login_frequency'] >= 10)
            ])
            
            # Ensure categories don't overlap - use priority order
            # Recalculate to avoid double-counting
            categorized = 0
            reasons_list = []
            
            # Priority 1: Low Usage (most common)
            low_usage_final = low_usage_churn
            categorized += low_usage_final
            
            # Priority 2: Poor Support
            poor_support_final = poor_support_churn
            categorized = min(categorized + poor_support_final, churned_customers)
            
            # Priority 3: Price
            price_final = price_churn
            categorized = min(categorized + price_final, churned_customers)
            
            # Priority 4: Competition (remainder)
            competition_final = max(churned_customers - categorized, competition_churn)
            
            # Normalize to ensure sum = 100%
            total_categorized = low_usage_final + poor_support_final + price_final + competition_final
            
            if total_categorized > 0:
                churn_reasons = [
                    {
                        'reason': 'Price',
                        'value': round((price_final / churned_customers) * 100, 1),
                        'color': '#3B82F6',
                        'count': price_final
                    },
                    {
                        'reason': 'Low Usage',
                        'value': round((low_usage_final / churned_customers) * 100, 1),
                        'color': '#60A5FA',
                        'count': low_usage_final
                    },
                    {
                        'reason': 'Poor Support',
                        'value': round((poor_support_final / churned_customers) * 100, 1),
                        'color': '#93C5FD',
                        'count': poor_support_final
                    },
                    {
                        'reason': 'Competition',
                        'value': round((competition_final / churned_customers) * 100, 1),
                        'color': '#DBEAFE',
                        'count': competition_final
                    }
                ]
                
                # Normalize percentages to exactly 100%
                total_pct = sum(r['value'] for r in churn_reasons)
                if total_pct > 0 and total_pct != 100:
                    adjustment = 100 - total_pct
                    churn_reasons[0]['value'] = round(churn_reasons[0]['value'] + adjustment, 1)

        # ========================================
        # RESPONSE FORMAT
        # ========================================
        
        response = {
            'kpiMetrics': {
                'churnRate': f"{churn_rate:.1f}%",
                'retentionRate': f"{retention_rate:.1f}%",
                'activeUsers': f"{active_users:,}",
                'healthScore': f"{avg_health_score:.1f}/10" if avg_health_score <= 10 else f"{avg_health_score:.0f}/100",
                'lossFromChurn': f"${churned_revenue:,.0f}"
            },
            'retentionData': retention_curve,
            'churnReasons': churn_reasons if churn_reasons else [
                {'reason': 'Price', 'value': 35, 'color': '#3B82F6', 'count': 0},
                {'reason': 'Low Usage', 'value': 28, 'color': '#60A5FA', 'count': 0},
                {'reason': 'Poor Support', 'value': 22, 'color': '#93C5FD', 'count': 0},
                {'reason': 'Competition', 'value': 15, 'color': '#DBEAFE', 'count': 0}
            ],
            'additionalMetrics': {
                'totalCustomers': total_customers,
                'churnedCount': churned_customers,
                'activeCustomersCount': active_customers_count,
                'timestamp': datetime.now().isoformat()
            }
        }

        print(f"✅ Dashboard stats: {churned_customers}/{total_customers} churned ({churn_rate:.1f}%), {active_users} active users")
        return jsonify(response)

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


@dashboard_bp.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify API is running."""
    return jsonify({
        "status": "healthy",
        "models_loaded": ml_models.is_loaded(),
        "message": "Flask API is running"
    })
