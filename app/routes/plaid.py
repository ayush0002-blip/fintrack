from flask import Blueprint, render_template
from flask_login import login_required

plaid_bp = Blueprint('plaid', __name__)

@plaid_bp.route('/')
@login_required
def index():
    return render_template('plaid.html')
