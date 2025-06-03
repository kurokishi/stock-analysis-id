# views/__init__.py
from .dashboard_view import show_dashboard
from .fundamental_view import show_fundamental_analysis
from .technical_view import show_technical_analysis
from .prediction_view import show_price_prediction
from .portfolio_view import portfolio_simulation
from .comparison_view import compare_stocks
from .news_sentiment import get_news_sentiment

__all__ = [
    'show_dashboard',
    'show_fundamental_analysis',
    'show_technical_analysis',
    'show_price_prediction',
    'portfolio_simulation',
    'compare_stocks',
    'get_news_sentiment'
]
