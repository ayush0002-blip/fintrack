from flask import Blueprint, render_template
from flask_login import login_required

budgets_bp = Blueprint('budgets', __name__)

@budgets_bp.route('/')
@login_required
def index():
    return render_template('budgets.html')
