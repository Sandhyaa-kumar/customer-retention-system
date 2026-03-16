"""Routes package for API endpoints."""

from .auth import auth_bp
from .customers import customers_bp
from .analytics import analytics_bp
from .dashboard import dashboard_bp

__all__ = ['auth_bp', 'customers_bp', 'analytics_bp', 'dashboard_bp']
