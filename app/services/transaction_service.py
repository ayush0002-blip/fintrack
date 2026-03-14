from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import func
from app.extensions import db
from app.models import Transaction


class TransactionService:
    @staticmethod
    def get_user_transactions(user_id, type=None, category=None, search=None):
        """
        Retrieve transactions for a user with optional filters.
        """
        query = Transaction.query.filter_by(user_id=user_id)

        if type:
            query = query.filter(Transaction.type == type)
        if category:
            query = query.filter(Transaction.category == category)
        if search:
            query = query.filter(
                (Transaction.title.ilike(f'%{search}%')) | 
                (Transaction.note.ilike(f'%{search}%'))
            )

        return query.order_by(Transaction.date.desc(), Transaction.id.desc()).all()

    @staticmethod
    def create_transaction(user_id, data):
        """
        Create a new transaction for a user.
        """
        transaction = Transaction(
            user_id=user_id,
            title=data.get('title'),
            amount=data.get('amount'),
            type=data.get('type'),
            category=data.get('category', 'Other'),
            date=data.get('date', date.today()),
            note=data.get('note')
        )
        db.session.add(transaction)
        db.session.commit()
        return transaction

    @staticmethod
    def update_transaction(transaction_id, data):
        """
        Update an existing transaction.
        """
        transaction = db.session.get(Transaction, transaction_id)
        if not transaction:
            return None

        transaction.title = data.get('title', transaction.title)
        transaction.amount = data.get('amount', transaction.amount)
        transaction.type = data.get('type', transaction.type)
        transaction.category = data.get('category', transaction.category)
        transaction.date = data.get('date', transaction.date)
        transaction.note = data.get('note', transaction.note)

        db.session.commit()
        return transaction

    @staticmethod
    def delete_transaction(transaction_id):
        """
        Delete a transaction.
        """
        transaction = db.session.get(Transaction, transaction_id)
        if transaction:
            db.session.delete(transaction)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_recent_transactions(user_id, limit=5):
        """
        Get the most recent transactions for a user.
        """
        return Transaction.query.filter_by(user_id=user_id)\
            .order_by(Transaction.date.desc(), Transaction.id.desc())\
            .limit(limit).all()

    @staticmethod
    def get_total_income(user_id, month=None, year=None):
        """
        Calculate total income for a specific month and year.
        If month/year not provided, returns overall total income.
        """
        query = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == Transaction.TYPE_INCOME
        )
        
        if month and year:
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year + 1, 1, 1)
            else:
                end_date = date(year, month + 1, 1)
            query = query.filter(Transaction.date >= start_date, Transaction.date < end_date)
            
        result = query.scalar()
        return result if result is not None else Decimal('0.00')

    @staticmethod
    def get_total_expenses(user_id, month=None, year=None):
        """
        Calculate total expenses for a specific month and year.
        If month/year not provided, returns overall total expenses.
        """
        query = db.session.query(func.sum(Transaction.amount)).filter(
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
            
        result = query.scalar()
        return result if result is not None else Decimal('0.00')
