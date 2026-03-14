from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import func
from app.extensions import db
from app.models import Transaction


class AnalyticsService:
    @staticmethod
    def monthly_income_expense(user_id, months=6):
        """
        Get income and expense totals for the last N months.
        """
        result = []
        today = date.today()
        
        for i in range(months - 1, -1, -1):
            # Calculate the first day of the month i months ago
            year = today.year
            month = today.month - i
            while month <= 0:
                month += 12
                year -= 1
            
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year + 1, 1, 1)
            else:
                end_date = date(year, month + 1, 1)
                
            # Query income
            income = db.session.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == user_id,
                Transaction.type == Transaction.TYPE_INCOME,
                Transaction.date >= start_date,
                Transaction.date < end_date
            ).scalar() or Decimal('0.00')
            
            # Query expense
            expense = db.session.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == user_id,
                Transaction.type == Transaction.TYPE_EXPENSE,
                Transaction.date >= start_date,
                Transaction.date < end_date
            ).scalar() or Decimal('0.00')
            
            result.append({
                'month': start_date.strftime('%b %Y'),
                'income': float(income),
                'expense': float(expense)
            })
            
        return result

    @staticmethod
    def spending_by_category(user_id, month=None, year=None):
        """
        Get a breakdown of expenses by category for a specific month/year.
        """
        query = db.session.query(
            Transaction.category, 
            func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.user_id == user_id,
            Transaction.type == Transaction.TYPE_EXPENSE
        )
        
        if month and year:
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year + 1, 1, 1)
            else:
                end_date = date(year, month + 1, 1)
            query = query.filter(Transaction.date >= start_date, Transaction.date < end_date)
            
        rows = query.group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc()).all()
        
        return [
            {'category': row.category, 'total': float(row.total)}
            for row in rows
        ]

    @staticmethod
    def savings_trend(user_id, months=6):
        """
        Get the savings (income - expense) trend for the last N months.
        """
        monthly_data = AnalyticsService.monthly_income_expense(user_id, months)
        
        return [
            {
                'month': data['month'],
                'savings': round(data['income'] - data['expense'], 2)
            }
            for data in monthly_data
        ]

    @staticmethod
    def get_summary_stats(user_id):
        """
        Retrieve high-level summary statistics for the user.
        """
        today = date.today()
        month_start = date(today.year, today.month, 1)
        
        # Monthly totals
        monthly_income = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == Transaction.TYPE_INCOME,
            Transaction.date >= month_start
        ).scalar() or Decimal('0.00')
        
        monthly_expense = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == Transaction.TYPE_EXPENSE,
            Transaction.date >= month_start
        ).scalar() or Decimal('0.00')
        
        # All time totals
        total_income = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == Transaction.TYPE_INCOME
        ).scalar() or Decimal('0.00')
        
        total_expense = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == Transaction.TYPE_EXPENSE
        ).scalar() or Decimal('0.00')
        
        # Average monthly spend (last 6 months)
        six_months_ago = today - timedelta(days=180)
        avg_spend_query = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == Transaction.TYPE_EXPENSE,
            Transaction.date >= six_months_ago
        ).scalar() or Decimal('0.00')
        
        avg_monthly_spend = avg_spend_query / 6
        
        # Savings Rate (Monthly)
        savings_rate = 0.0
        if monthly_income > 0:
            savings_rate = float(((monthly_income - monthly_expense) / monthly_income) * 100)
            
        return {
            'monthly_income': float(monthly_income),
            'monthly_expense': float(monthly_expense),
            'total_income': float(total_income),
            'total_expense': float(total_expense),
            'net_savings': float(total_income - total_expense),
            'avg_monthly_spend': round(float(avg_monthly_spend), 2),
            'savings_rate': round(max(0.0, savings_rate), 1)
        }
