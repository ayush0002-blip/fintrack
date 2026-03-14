from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.services.dashboard_service import get_dashboard_context

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    ctx = get_dashboard_context(current_user)
    return render_template('dashboard.html', **ctx)
