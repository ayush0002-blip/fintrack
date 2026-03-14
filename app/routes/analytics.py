from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.services.analytics_service import AnalyticsService
import json

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/')
@login_required
def index():
    user_id = current_user.id
    
    # Fetch data from AnalyticsService
    monthly_trends = AnalyticsService.monthly_income_expense(user_id)
    category_spending = AnalyticsService.spending_by_category(user_id)
    savings_trend = AnalyticsService.savings_trend(user_id)
    summary_stats = AnalyticsService.get_summary_stats(user_id)
    
    # Prepare data for Chart.js (JSON strings)
    chart_data = {
        'trends': {
            'labels': [d['month'] for d in monthly_trends],
            'income': [d['income'] for d in monthly_trends],
            'expense': [d['expense'] for d in monthly_trends]
        },
        'categories': {
            'labels': [c['category'] for c in category_spending],
            'data': [c['total'] for c in category_spending]
        },
        'savings': {
            'labels': [s['month'] for s in savings_trend],
            'data': [s['savings'] for s in savings_trend]
        }
    }
    
    return render_template(
        'analytics.html',
        summary=summary_stats,
        chart_data_json=json.dumps(chart_data),
        category_spending=category_spending[:5] # Top 5 for the table
    )
