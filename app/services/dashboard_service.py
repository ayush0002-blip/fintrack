"""
dashboard_service.py
~~~~~~~~~~~~~~~~~~~~
Pure-query helper functions that gather all dashboard data for one user.
All functions accept a User ORM object and return plain Python dicts/lists
so the route and template stay thin.
"""

from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import func
from app.extensions import db
from app.models import Transaction, Budget, Subscription


def _zero():
    return Decimal('0.00')


# ─────────────────────────────────────────────────────────────
# Lifetime totals
# ─────────────────────────────────────────────────────────────
def get_lifetime_totals(user):
    """Return total income, expenses, and net balance across all time."""
    rows = (
        db.session.query(Transaction.type, func.sum(Transaction.amount))
        .filter(Transaction.user_id == user.id)
        .group_by(Transaction.type)
        .all()
    )
    totals = {r[0]: r[1] or _zero() for r in rows}
    income   = totals.get(Transaction.TYPE_INCOME,  _zero())
    expenses = totals.get(Transaction.TYPE_EXPENSE, _zero())
    return {
        'total_income':   income,
        'total_expenses': expenses,
        'net_balance':    income - expenses,
    }


# ─────────────────────────────────────────────────────────────
# This month's stats
# ─────────────────────────────────────────────────────────────
def get_current_month_stats(user):
    """Spending and income for the current calendar month."""
    today = date.today()
    month_start = today.replace(day=1)

    rows = (
        db.session.query(Transaction.type, func.sum(Transaction.amount))
        .filter(
            Transaction.user_id == user.id,
            Transaction.date    >= month_start,
            Transaction.date    <= today,
        )
        .group_by(Transaction.type)
        .all()
    )
    totals  = {r[0]: r[1] or _zero() for r in rows}
    income  = totals.get(Transaction.TYPE_INCOME,  _zero())
    expense = totals.get(Transaction.TYPE_EXPENSE, _zero())
    return {
        'month_income':   income,
        'month_expenses': expense,
        'month_net':      income - expense,
        'month_label':    today.strftime('%B %Y'),
    }


# ─────────────────────────────────────────────────────────────
# Recent transactions
# ─────────────────────────────────────────────────────────────
def get_recent_transactions(user, limit=8):
    """Last `limit` transactions ordered newest first."""
    return (
        user.transactions
        .order_by(Transaction.date.desc(), Transaction.id.desc())
        .limit(limit)
        .all()
    )


# ─────────────────────────────────────────────────────────────
# Budget summary
# ─────────────────────────────────────────────────────────────
def get_budget_summary(user, limit=6):
    """
    For each budget in the current month return:
        category, monthly_limit, spent, remaining, pct_used
    """
    today = date.today()
    budgets = (
        user.budgets
        .filter_by(month=today.month, year=today.year)
        .limit(limit)
        .all()
    )
    result = []
    for b in budgets:
        spent = (
            db.session.query(func.sum(Transaction.amount))
            .filter(
                Transaction.user_id  == user.id,
                Transaction.type     == Transaction.TYPE_EXPENSE,
                Transaction.category == b.category,
                Transaction.date     >= today.replace(day=1),
                Transaction.date     <= today,
            )
            .scalar() or _zero()
        )
        limit_val = b.monthly_limit or _zero()
        pct = float(spent / limit_val * 100) if limit_val else 0.0
        result.append({
            'id':            b.id,
            'category':      b.category,
            'monthly_limit': limit_val,
            'spent':         spent,
            'remaining':     max(limit_val - spent, _zero()),
            'pct_used':      min(round(pct, 1), 100.0),
            'over_budget':   spent > limit_val,
        })
    return result


# ─────────────────────────────────────────────────────────────
# Active subscriptions
# ─────────────────────────────────────────────────────────────
def get_active_subscriptions(user, limit=5):
    """Active subscriptions ordered by nearest due date."""
    return (
        user.subscriptions
        .filter_by(status=Subscription.STATUS_ACTIVE)
        .order_by(Subscription.next_due_date.asc())
        .limit(limit)
        .all()
    )


def get_monthly_subscription_cost(user):
    """Rough total monthly cost: sum active, normalise weekly→monthly, yearly→monthly."""
    subs = (
        user.subscriptions
        .filter_by(status=Subscription.STATUS_ACTIVE)
        .all()
    )
    total = _zero()
    for s in subs:
        if s.billing_cycle == Subscription.CYCLE_MONTHLY:
            total += s.amount
        elif s.billing_cycle == Subscription.CYCLE_WEEKLY:
            total += s.amount * Decimal('4.33')
        elif s.billing_cycle == Subscription.CYCLE_YEARLY:
            total += s.amount / Decimal('12')
    return round(total, 2)


# ─────────────────────────────────────────────────────────────
# Master collector
# ─────────────────────────────────────────────────────────────
def get_dashboard_context(user):
    """Return a single dict ready for `render_template`."""
    lifetime   = get_lifetime_totals(user)
    this_month = get_current_month_stats(user)
    budgets    = get_budget_summary(user)
    subs       = get_active_subscriptions(user)

    return {
        # Lifetime
        'total_income':          lifetime['total_income'],
        'total_expenses':        lifetime['total_expenses'],
        'net_balance':           lifetime['net_balance'],
        # This month
        'month_income':          this_month['month_income'],
        'month_expenses':        this_month['month_expenses'],
        'month_net':             this_month['month_net'],
        'month_label':           this_month['month_label'],
        # Lists
        'recent_transactions':   get_recent_transactions(user),
        'budget_cards':          budgets,
        'active_subscriptions':  subs,
        'monthly_sub_cost':      get_monthly_subscription_cost(user),
        # Counts / flags
        'has_transactions':      user.transactions.count() > 0,
        'has_budgets':           bool(budgets),
        'has_subscriptions':     bool(subs),
    }
