"""
Flask Application Entry Point
Minimal app.py that imports and registers all routes.
Database connection, ML models, and business logic are in separate modules.
"""

from flask import Flask
from flask_cors import CORS

# Import route blueprints
from routes import customers_bp, analytics_bp, dashboard_bp

# Import services to initialize them
from services import ml_models

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Register blueprints
app.register_blueprint(customers_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(dashboard_bp)


# Run Flask application
if __name__ == '__main__':
    print("🚀 Starting Flask Server on http://127.0.0.1:5000")
    print("📡 CORS enabled for React Frontend")
    print(f"✅ ML Models loaded: {ml_models.is_loaded()}")
    app.run(debug=True, port=5000)