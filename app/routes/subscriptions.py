from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Subscription
from app.forms import SubscriptionForm
from app.services.subscription_service import SubscriptionService

subscriptions_bp = Blueprint('subscriptions', __name__)


# ─────────────────────────────────────────────────────────────
# List
# ─────────────────────────────────────────────────────────────
@subscriptions_bp.route('/')
@login_required
def index():
    subs = SubscriptionService.get_all_enriched(current_user)
    monthly_total = SubscriptionService.get_monthly_total(current_user)
    upcoming_count = SubscriptionService.get_upcoming_count(current_user)
    
    return render_template(
        'subscriptions.html', 
        subscriptions=subs,
        monthly_total=monthly_total,
        upcoming_count=upcoming_count
    )


# ─────────────────────────────────────────────────────────────
# Create
# ─────────────────────────────────────────────────────────────
@subscriptions_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    form = SubscriptionForm()
    if form.validate_on_submit():
        sub = Subscription(
            user_id       = current_user.id,
            name          = form.name.data,
            amount        = form.amount.data,
            billing_cycle = form.billing_cycle.data,
            next_due_date = form.next_due_date.data,
            status        = form.status.data,
        )
        db.session.add(sub)
        db.session.commit()
        flash('Subscription added.', 'success')
        return redirect(url_for('subscriptions.index'))
    return render_template('subscriptions.html', form=form, action='New', show_modal=True)


# ─────────────────────────────────────────────────────────────
# Edit
# ─────────────────────────────────────────────────────────────
@subscriptions_bp.route('/<int:sub_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(sub_id):
    sub = db.session.get(Subscription, sub_id)
    if not sub or sub.user_id != current_user.id:
        abort(404)
    form = SubscriptionForm(obj=sub)
    if form.validate_on_submit():
        form.populate_obj(sub)
        db.session.commit()
        flash('Subscription updated.', 'success')
        return redirect(url_for('subscriptions.index'))
    return render_template('subscriptions.html', form=form, sub_id=sub_id, action='Edit', show_modal=True)


# ─────────────────────────────────────────────────────────────
# Delete
# ─────────────────────────────────────────────────────────────
@subscriptions_bp.route('/<int:sub_id>/delete', methods=['POST'])
@login_required
def delete(sub_id):
    sub = db.session.get(Subscription, sub_id)
    if not sub or sub.user_id != current_user.id:
        abort(404)
    db.session.delete(sub)
    db.session.commit()
    flash('Subscription deleted.', 'info')
    return redirect(url_for('subscriptions.index'))
