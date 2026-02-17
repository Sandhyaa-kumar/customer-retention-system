"""Routes package for API endpoints."""

from .customers import customers_bp
from .analytics import analytics_bp
from .dashboard import dashboard_bp

__all__ = ['customers_bp', 'analytics_bp', 'dashboard_bp']
