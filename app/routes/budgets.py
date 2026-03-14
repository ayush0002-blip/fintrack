from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Budget, Transaction
from app.forms import BudgetForm
from app.services.budget_service import enrich_budgets, get_month_filter_options

budgets_bp = Blueprint('budgets', __name__)


# ─────────────────────────────────────────────────────────────
# List
# ─────────────────────────────────────────────────────────────
@budgets_bp.route('/')
@login_required
def index():
    # Optional month/year filter via query param (default: all months)
    today    = date.today()
    sel_month = request.args.get('month', type=int)
    sel_year  = request.args.get('year',  type=int)

    q = current_user.budgets
    if sel_month and sel_year:
        q = q.filter(Budget.month == sel_month, Budget.year == sel_year)

    budgets_raw = q.order_by(Budget.year.desc(), Budget.month.desc(),
                              Budget.category.asc()).all()
    budget_cards = enrich_budgets(budgets_raw, current_user.id)

    # Summary totals across shown budgets
    total_limit   = sum(b['monthly_limit'] for b in budget_cards)
    total_spent   = sum(b['spent'] for b in budget_cards)
    over_count    = sum(1 for b in budget_cards if b['over_budget'])

    return render_template(
        'budgets/index.html',
        budget_cards=budget_cards,
        month_options=get_month_filter_options(current_user.id),
        sel_month=sel_month,
        sel_year=sel_year,
        total_limit=total_limit,
        total_spent=total_spent,
        over_count=over_count,
        today=today,
    )


# ─────────────────────────────────────────────────────────────
# Create
# ─────────────────────────────────────────────────────────────
@budgets_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    today = date.today()
    form  = BudgetForm()
    # Pre-fill month/year to current month if not already set
    if request.method == 'GET':
        form.month.data = today.month
        form.year.data  = today.year

    if form.validate_on_submit():
        # Check for duplicate (same user + category + month + year)
        exists = Budget.query.filter_by(
            user_id  = current_user.id,
            category = form.category.data,
            month    = form.month.data,
            year     = form.year.data,
        ).first()
        if exists:
            flash(
                f'A budget for "{form.category.data}" in '
                f'{date(form.year.data, form.month.data, 1).strftime("%B %Y")} '
                f'already exists. Edit it instead.',
                'warning',
            )
            return redirect(url_for('budgets.edit', budget_id=exists.id))

        budget = Budget(
            user_id       = current_user.id,
            category      = form.category.data,
            monthly_limit = form.monthly_limit.data,
            month         = form.month.data,
            year          = form.year.data,
        )
        db.session.add(budget)
        db.session.commit()
        month_label = date(budget.year, budget.month, 1).strftime('%B %Y')
        flash(f'Budget for "{budget.category}" ({month_label}) created.', 'success')
        return redirect(url_for('budgets.index'))
    return render_template('budgets/form.html', form=form, action='New Budget',
                           budget=None)


# ─────────────────────────────────────────────────────────────
# Edit
# ─────────────────────────────────────────────────────────────
@budgets_bp.route('/<int:budget_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(budget_id):
    budget = db.session.get(Budget, budget_id)
    if not budget or budget.user_id != current_user.id:
        abort(404)
    form = BudgetForm(obj=budget)
    if form.validate_on_submit():
        budget.category      = form.category.data
        budget.monthly_limit = form.monthly_limit.data
        budget.month         = form.month.data
        budget.year          = form.year.data
        db.session.commit()
        month_label = date(budget.year, budget.month, 1).strftime('%B %Y')
        flash(f'Budget for "{budget.category}" ({month_label}) updated.', 'success')
        return redirect(url_for('budgets.index'))
    return render_template('budgets/form.html', form=form, action='Edit Budget',
                           budget=budget)


# ─────────────────────────────────────────────────────────────
# Delete
# ─────────────────────────────────────────────────────────────
@budgets_bp.route('/<int:budget_id>/delete', methods=['POST'])
@login_required
def delete(budget_id):
    budget = db.session.get(Budget, budget_id)
    if not budget or budget.user_id != current_user.id:
        abort(404)
    label = f'"{budget.category}" ({date(budget.year, budget.month, 1).strftime("%B %Y")})'
    db.session.delete(budget)
    db.session.commit()
    flash(f'Budget {label} deleted.', 'info')
    return redirect(url_for('budgets.index'))
