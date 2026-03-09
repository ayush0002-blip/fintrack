from flask import Blueprint, render_template
from flask_login import login_required

subscriptions_bp = Blueprint('subscriptions', __name__)

@subscriptions_bp.route('/')
@login_required
def index():
    return render_template('subscriptions.html')
