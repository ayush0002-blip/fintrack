from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db, login_manager


# ─────────────────────────────────────────────────────────────
# User Loader (required by Flask-Login)
# ─────────────────────────────────────────────────────────────
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ─────────────────────────────────────────────────────────────
# User Model
# ─────────────────────────────────────────────────────────────
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    full_name     = db.Column(db.String(128), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # ── Relationships ────────────────────────────────────────
    transactions  = db.relationship('Transaction',  backref='user', lazy='dynamic', cascade='all, delete-orphan')
    budgets       = db.relationship('Budget',       backref='user', lazy='dynamic', cascade='all, delete-orphan')
    subscriptions = db.relationship('Subscription', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    plaid_items   = db.relationship('PlaidItem',    backref='user', lazy='dynamic', cascade='all, delete-orphan')

    # ── Password helpers ────────────────────────────────────
    def set_password(self, password: str) -> None:
        """Hash and store password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify a plain-text password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    # ── Dunder ───────────────────────────────────────────────
    def __repr__(self) -> str:
        return f'<User id={self.id} email={self.email!r}>'


# ─────────────────────────────────────────────────────────────
# Plaid Item Model
# ─────────────────────────────────────────────────────────────
class PlaidItem(db.Model):
    __tablename__ = 'plaid_items'

    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    access_token     = db.Column(db.String(256), nullable=False)
    item_id          = db.Column(db.String(256), nullable=False)
    institution_name = db.Column(db.String(128))
    created_at       = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self) -> str:
        return f'<PlaidItem id={self.id} item_id={self.item_id!r}>'


# ─────────────────────────────────────────────────────────────
# Transaction Model
# ─────────────────────────────────────────────────────────────
class Transaction(db.Model):
    __tablename__ = 'transactions'

    # Valid values for the `type` column
    TYPE_INCOME  = 'income'
    TYPE_EXPENSE = 'expense'

    # Valid category labels (used for UI dropdowns & budget matching)
    CATEGORIES = [
        'Food & Dining',
        'Transport',
        'Housing',
        'Healthcare',
        'Entertainment',
        'Shopping',
        'Education',
        'Savings',
        'Salary',
        'Freelance',
        'Investment',
        'Other',
    ]

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    title      = db.Column(db.String(200), nullable=False)
    amount     = db.Column(db.Numeric(12, 2), nullable=False)
    type       = db.Column(db.String(10), nullable=False)           # 'income' | 'expense'
    category   = db.Column(db.String(64), nullable=False, default='Other')
    date       = db.Column(db.Date, nullable=False)
    note       = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self) -> str:
        return f'<Transaction id={self.id} type={self.type!r} amount={self.amount}>'


# ─────────────────────────────────────────────────────────────
# Budget Model
# ─────────────────────────────────────────────────────────────
class Budget(db.Model):
    __tablename__ = 'budgets'

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    category      = db.Column(db.String(64), nullable=False)
    monthly_limit = db.Column(db.Numeric(12, 2), nullable=False)
    month         = db.Column(db.Integer, nullable=False)           # 1–12
    year          = db.Column(db.Integer, nullable=False)
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # One budget per category per month/year per user
    __table_args__ = (
        db.UniqueConstraint('user_id', 'category', 'month', 'year', name='uq_budget_user_cat_month'),
    )

    def __repr__(self) -> str:
        return f'<Budget id={self.id} category={self.category!r} {self.month}/{self.year}>'


# ─────────────────────────────────────────────────────────────
# Subscription Model
# ─────────────────────────────────────────────────────────────
class Subscription(db.Model):
    __tablename__ = 'subscriptions'

    # Billing cycle options
    CYCLE_MONTHLY  = 'monthly'
    CYCLE_YEARLY   = 'yearly'
    CYCLE_WEEKLY   = 'weekly'
    BILLING_CYCLES = [CYCLE_WEEKLY, CYCLE_MONTHLY, CYCLE_YEARLY]

    # Status options
    STATUS_ACTIVE   = 'active'
    STATUS_PAUSED   = 'paused'
    STATUS_CANCELLED = 'cancelled'

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    name          = db.Column(db.String(128), nullable=False)
    amount        = db.Column(db.Numeric(10, 2), nullable=False)
    billing_cycle = db.Column(db.String(16), nullable=False, default=CYCLE_MONTHLY)
    next_due_date = db.Column(db.Date, nullable=False)
    status        = db.Column(db.String(16), nullable=False, default=STATUS_ACTIVE)
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self) -> str:
        return f'<Subscription id={self.id} name={self.name!r} status={self.status!r}>'
