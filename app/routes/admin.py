from flask import Blueprint, render_template, request, current_app
from flask_login import login_required
from app.models import User, Transaction, Budget, Subscription
from app.utils.decorators import admin_required
from app.extensions import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/clients')
@login_required
@admin_required
def clients():
    clients = User.query.filter_by(is_admin=False).all()
    
    client_data = []
    for client in clients:
        # Sum transactions by type
        income_sum = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.user_id == client.id, Transaction.type == 'income'
        ).scalar() or 0
        expense_sum = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.user_id == client.id, Transaction.type == 'expense'
        ).scalar() or 0
        
        # Sum monthly subscriptions
        subs_sum = db.session.query(db.func.sum(Subscription.amount)).filter(
            Subscription.user_id == client.id, Subscription.status == 'active'
        ).scalar() or 0
        
        client_data.append({
            'user': client,
            'total_income': float(income_sum),
            'total_expense': float(expense_sum),
            'total_subs': float(subs_sum)
        })
        
    return render_template('admin/clients.html', clients=client_data)

@admin_bp.route('/clients/<int:user_id>')
@login_required
@admin_required
def client_detail(user_id):
    client = User.query.get_or_404(user_id)
    transactions = Transaction.query.filter_by(user_id=client.id).order_by(Transaction.date.desc()).limit(50).all()
    budgets = Budget.query.filter_by(user_id=client.id).all()
    subscriptions = Subscription.query.filter_by(user_id=client.id).all()
    
    # Calculate summary stats
    income_sum = sum(tx.amount for tx in transactions if tx.type == 'income')
    expense_sum = sum(tx.amount for tx in transactions if tx.type == 'expense')
    subs_sum = sum(sub.amount for sub in subscriptions if sub.status == 'active')
    total_budget = sum(b.monthly_limit for b in budgets)
    
    return render_template('admin/client_detail.html', 
                          client=client, 
                          transactions=transactions, 
                          budgets=budgets, 
                          subscriptions=subscriptions,
                          income_sum=float(income_sum),
                          expense_sum=float(expense_sum),
                          subs_sum=float(subs_sum),
                          total_budget=float(total_budget))
