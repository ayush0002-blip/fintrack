from datetime import date
from decimal import Decimal
from sqlalchemy import func
from app.extensions import db
from app.models import Transaction, Budget


def _zero():
    return Decimal('0.00')


def get_spending_for_budget(user_id: int, category: str, month: int, year: int) -> Decimal:
    """
    Sum of expense transactions for `user_id` in `category` during `month/year`.
    """
    month_start = date(year, month, 1)
    if month == 12:
        month_end = date(year + 1, 1, 1)
    else:
        month_end = date(year, month + 1, 1)

    total = (
        db.session.query(func.sum(Transaction.amount))
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == Transaction.TYPE_EXPENSE,
            Transaction.category == category,
            Transaction.date >= month_start,
            Transaction.date < month_end,
        )
        .scalar()
    )
    return total if total is not None else Decimal('0.00')


def enrich_budget(budget: Budget) -> dict:
    """
    Return a dict with all display-ready fields for one budget.
    """
    limit = budget.monthly_limit or _zero()
    spent = get_spending_for_budget(budget.user_id, budget.category, budget.month, budget.year)
    remaining = max(limit - spent, _zero())
    pct = float(spent / limit * 100) if limit else 0.0
    pct_capped = min(round(pct, 1), 100.0)
    over_budget = spent > limit
    near_limit = not over_budget and pct >= 80.0

    if over_budget:
        status = 'exceeded'
    elif near_limit:
        status = 'warning'
    else:
        status = 'ok'

    return {
        'id': budget.id,
        'category': budget.category,
        'monthly_limit': limit,
        'month': budget.month,
        'year': budget.year,
        'month_label': date(budget.year, budget.month, 1).strftime('%B %Y'),
        'spent': spent,
        'remaining': remaining,
        'pct_used': pct_capped,
        'over_budget': over_budget,
        'near_limit': near_limit,
        'status': status,
    }


def enrich_budgets(budgets: list, user_id: int = None) -> list:
    """Convenience for enriching a list of budget models."""
    return [enrich_budget(b) for b in budgets]


def get_month_filter_options(user_id: int) -> list[dict]:
    """
    Return distinct month/year combos that have at least one budget.
    """
    rows = (
        db.session.query(Budget.year, Budget.month)
        .filter(Budget.user_id == user_id)
        .distinct()
        .order_by(Budget.year.desc(), Budget.month.desc())
        .all()
    )
    return [
        {
            'year': year,
            'month': month,
            'label': date(year, month, 1).strftime('%B %Y'),
        }
        for year, month in rows
    ]


class BudgetService:
    """Legacy wrapper for consistency if needed, but the project prefers top-level functions."""
    @staticmethod
    def get_user_budgets(user_id, month=None, year=None):
        query = Budget.query.filter_by(user_id=user_id)
        if month:
            query = query.filter(Budget.month == month)
        if year:
            query = query.filter(Budget.year == year)
        
        budgets = query.order_by(Budget.year.desc(), Budget.month.desc()).all()
        return [enrich_budget(b) for b in budgets]

    @staticmethod
    def create_budget(user_id, data):
        budget = Budget(
            user_id=user_id,
            category=data.get('category'),
            monthly_limit=data.get('monthly_limit'),
            month=data.get('month', date.today().month),
            year=data.get('year', date.today().year)
        )
        db.session.add(budget)
        db.session.commit()
        return budget

    @staticmethod
    def update_budget(budget_id, data):
        budget = db.session.get(Budget, budget_id)
        if not budget:
            return None

        budget.category = data.get('category', budget.category)
        budget.monthly_limit = data.get('monthly_limit', budget.monthly_limit)
        budget.month = data.get('month', budget.month)
        budget.year = data.get('year', budget.year)

        db.session.commit()
        return budget

    @staticmethod
    def delete_budget(budget_id):
        budget = db.session.get(Budget, budget_id)
        if budget:
            db.session.delete(budget)
            db.session.commit()
            return True
        return False
