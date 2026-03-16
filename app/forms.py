from datetime import date
from flask_wtf import FlaskForm
from wtforms import (
    StringField, DecimalField, SelectField,
    DateField, TextAreaField, IntegerField, SubmitField,
    PasswordField, RadioField
)
from wtforms.validators import (
    DataRequired, Length, NumberRange, Optional, ValidationError,
    Email, EqualTo
)
from app.models import Transaction, Budget, Subscription


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
def _category_choices():
    """Return WTForms-compatible choice tuples from the Transaction model."""
    return [(c, c) for c in Transaction.CATEGORIES]


# ─────────────────────────────────────────────────────────────
# TransactionForm
# ─────────────────────────────────────────────────────────────
class TransactionForm(FlaskForm):
    """Create or edit a single income / expense transaction."""

    title = StringField(
        'Title',
        validators=[
            DataRequired(message='A title is required.'),
            Length(max=200, message='Title must be 200 characters or fewer.'),
        ],
        render_kw={'placeholder': 'e.g. Coffee at Starbucks'},
    )

    amount = DecimalField(
        'Amount',
        places=2,
        validators=[
            DataRequired(message='Amount is required.'),
            NumberRange(min=0.01, message='Amount must be greater than zero.'),
        ],
        render_kw={'placeholder': '0.00', 'step': '0.01', 'min': '0.01'},
    )

    type = RadioField(
        'Type',
        choices=[
            (Transaction.TYPE_INCOME,  'Income'),
            (Transaction.TYPE_EXPENSE, 'Expense'),
        ],
        validators=[DataRequired()],
    )

    category = SelectField(
        'Category',
        choices=_category_choices,   # callable — evaluated lazily per request
        validators=[DataRequired()],
    )

    date = DateField(
        'Date',
        validators=[DataRequired(message='Please pick a date.')],
    )

    note = TextAreaField(
        'Note',
        validators=[Optional(), Length(max=1000)],
        render_kw={'rows': 3, 'placeholder': 'Optional note…'},
    )

    submit = SubmitField('Save Transaction')

    # ── Cross-field / custom validators ─────────────────────
    def validate_date(self, field):
        if field.data and field.data > date.today():
            raise ValidationError('Transaction date cannot be in the future.')


# ─────────────────────────────────────────────────────────────
# BudgetForm
# ─────────────────────────────────────────────────────────────
class BudgetForm(FlaskForm):
    """Create or edit a monthly budget limit for a category."""

    category = SelectField(
        'Category',
        choices=_category_choices,
        validators=[DataRequired()],
    )

    monthly_limit = DecimalField(
        'Monthly Limit',
        places=2,
        validators=[
            DataRequired(message='A monthly limit is required.'),
            NumberRange(min=0.01, message='Monthly limit must be greater than zero.'),
        ],
        render_kw={'placeholder': '0.00', 'step': '0.01', 'min': '0.01'},
    )

    month = SelectField(
        'Month',
        choices=[(m, date(2000, m, 1).strftime('%B')) for m in range(1, 13)],
        coerce=int,
        validators=[DataRequired()],
    )

    year = IntegerField(
        'Year',
        validators=[
            DataRequired(message='Year is required.'),
            NumberRange(min=2000, max=2100, message='Enter a valid year (2000–2100).'),
        ],
        render_kw={'placeholder': str(date.today().year)},
    )

    submit = SubmitField('Save Budget')

    def validate_year(self, field):
        today = date.today()
        if field.data and self.month.data:
            entered = date(field.data, self.month.data, 1)
            current  = date(today.year, today.month, 1)
            if entered < current:
                raise ValidationError('Budget month/year cannot be in the past.')


# ─────────────────────────────────────────────────────────────
# SubscriptionForm
# ─────────────────────────────────────────────────────────────
class SubscriptionForm(FlaskForm):
    """Create or edit a recurring subscription."""

    name = StringField(
        'Service Name',
        validators=[
            DataRequired(message='Service name is required.'),
            Length(max=128, message='Name must be 128 characters or fewer.'),
        ],
        render_kw={'placeholder': 'e.g. Netflix, Spotify…'},
    )

    amount = DecimalField(
        'Amount',
        places=2,
        validators=[
            DataRequired(message='Amount is required.'),
            NumberRange(min=0.01, message='Amount must be greater than zero.'),
        ],
        render_kw={'placeholder': '0.00', 'step': '0.01', 'min': '0.01'},
    )

    billing_cycle = SelectField(
        'Billing Cycle',
        choices=[
            (Subscription.CYCLE_WEEKLY,  'Weekly'),
            (Subscription.CYCLE_MONTHLY, 'Monthly'),
            (Subscription.CYCLE_YEARLY,  'Yearly'),
        ],
        validators=[DataRequired()],
    )

    next_due_date = DateField(
        'Next Due Date',
        validators=[DataRequired(message='Please set the next due date.')],
    )

    status = SelectField(
        'Status',
        choices=[
            (Subscription.STATUS_ACTIVE,    'Active'),
            (Subscription.STATUS_PAUSED,    'Paused'),
            (Subscription.STATUS_CANCELLED, 'Cancelled'),
        ],
        default=Subscription.STATUS_ACTIVE,
        validators=[DataRequired()],
    )

    submit = SubmitField('Save Subscription')

    def validate_next_due_date(self, field):
        if field.data and field.data < date.today():
            raise ValidationError('Next due date must be today or in the future.')


# ─────────────────────────────────────────────────────────────
# Settings Forms
# ─────────────────────────────────────────────────────────────
class ProfileForm(FlaskForm):
    """Update user profile information."""
    full_name = StringField(
        'Full Name',
        validators=[
            DataRequired(message='Full name is required.'),
            Length(max=128, message='Name must be 128 characters or fewer.'),
        ],
        render_kw={'placeholder': 'Full Name'}
    )
    email = StringField(
        'Email Address',
        validators=[
            DataRequired(message='Email is required.'),
            Email(message='Invalid email address.'),
            Length(max=120, message='Email must be 120 characters or fewer.'),
        ],
        render_kw={'placeholder': 'email@example.com'}
    )
    submit = SubmitField('Update Profile')


class ChangePasswordForm(FlaskForm):
    """Securely change user password."""
    current_password = PasswordField(
        'Current Password',
        validators=[DataRequired(message='Current password is required.')],
        render_kw={'placeholder': '••••••••'}
    )
    new_password = PasswordField(
        'New Password',
        validators=[
            DataRequired(message='New password is required.'),
            Length(min=8, message='Password must be at least 8 characters long.'),
        ],
        render_kw={'placeholder': '••••••••'}
    )
    confirm_password = PasswordField(
        'Confirm New Password',
        validators=[
            DataRequired(message='Please confirm your new password.'),
            EqualTo('new_password', message='Passwords must match.'),
        ],
        render_kw={'placeholder': '••••••••'}
    )
    submit = SubmitField('Change Password')
