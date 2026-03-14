from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from sqlalchemy import or_
from app.extensions import db
from app.models import Transaction
from app.forms import TransactionForm

transactions_bp = Blueprint('transactions', __name__)


# ─────────────────────────────────────────────────────────────
# List  (with search + filter + sort)
# ─────────────────────────────────────────────────────────────
@transactions_bp.route('/')
@login_required
def index():
    # ── Read query-string params ──────────────────────────
    search   = request.args.get('q',        '').strip()
    typ      = request.args.get('type',     '')      # 'income' | 'expense' | ''
    category = request.args.get('category', '')
    sort     = request.args.get('sort',     'date_desc')

    # ── Base query scoped to current user ─────────────────
    q = current_user.transactions

    # ── Apply filters ─────────────────────────────────────
    if typ in (Transaction.TYPE_INCOME, Transaction.TYPE_EXPENSE):
        q = q.filter(Transaction.type == typ)

    if category and category in Transaction.CATEGORIES:
        q = q.filter(Transaction.category == category)

    if search:
        pattern = f'%{search}%'
        q = q.filter(
            or_(
                Transaction.title.ilike(pattern),
                Transaction.note.ilike(pattern),
            )
        )

    # ── Apply sort ────────────────────────────────────────
    sort_map = {
        'date_desc':   Transaction.date.desc(),
        'date_asc':    Transaction.date.asc(),
        'amount_desc': Transaction.amount.desc(),
        'amount_asc':  Transaction.amount.asc(),
        'title_asc':   Transaction.title.asc(),
    }
    q = q.order_by(sort_map.get(sort, Transaction.date.desc()),
                   Transaction.id.desc())

    transactions = q.all()

    # ── Summary totals (filtered set) ─────────────────────
    income   = sum(t.amount for t in transactions if t.type == Transaction.TYPE_INCOME)
    expenses = sum(t.amount for t in transactions if t.type == Transaction.TYPE_EXPENSE)

    return render_template(
        'transactions/index.html',
        transactions=transactions,
        categories=Transaction.CATEGORIES,
        # active filters (pass back for UI state)
        q=search, typ=typ, category=category, sort=sort,
        # summary
        filtered_income=income,
        filtered_expenses=expenses,
        filtered_net=income - expenses,
    )


# ─────────────────────────────────────────────────────────────
# Create
# ─────────────────────────────────────────────────────────────
@transactions_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    form = TransactionForm()
    if form.validate_on_submit():
        txn = Transaction(
            user_id  = current_user.id,
            title    = form.title.data.strip(),
            amount   = form.amount.data,
            type     = form.type.data,
            category = form.category.data,
            date     = form.date.data,
            note     = form.note.data.strip() or None,
        )
        db.session.add(txn)
        db.session.commit()
        flash(f'Transaction "{txn.title}" added successfully.', 'success')
        return redirect(url_for('transactions.index'))
    return render_template('transactions/form.html', form=form, action='Add Transaction',
                           txn=None)


# ─────────────────────────────────────────────────────────────
# Edit
# ─────────────────────────────────────────────────────────────
@transactions_bp.route('/<int:txn_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(txn_id):
    txn = db.session.get(Transaction, txn_id)
    if not txn or txn.user_id != current_user.id:
        abort(404)
    form = TransactionForm(obj=txn)
    if form.validate_on_submit():
        txn.title    = form.title.data.strip()
        txn.amount   = form.amount.data
        txn.type     = form.type.data
        txn.category = form.category.data
        txn.date     = form.date.data
        txn.note     = form.note.data.strip() or None
        db.session.commit()
        flash(f'Transaction "{txn.title}" updated.', 'success')
        return redirect(url_for('transactions.index'))
    return render_template('transactions/form.html', form=form, action='Edit Transaction',
                           txn=txn)


# ─────────────────────────────────────────────────────────────
# Delete
# ─────────────────────────────────────────────────────────────
@transactions_bp.route('/<int:txn_id>/delete', methods=['POST'])
@login_required
def delete(txn_id):
    txn = db.session.get(Transaction, txn_id)
    if not txn or txn.user_id != current_user.id:
        abort(404)
    title = txn.title
    db.session.delete(txn)
    db.session.commit()
    flash(f'Transaction "{title}" deleted.', 'info')
    return redirect(url_for('transactions.index'))
