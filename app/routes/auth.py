from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models import User

auth_bp = Blueprint('auth', __name__)


# ─────────────────────────────────────────────────────────────
# Signup
# ─────────────────────────────────────────────────────────────
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email     = request.form.get('email', '').strip().lower()
        password  = request.form.get('password', '')
        confirm   = request.form.get('confirm_password', '')

        # ── Validation ───────────────────────────────────────
        errors = []
        if not full_name:
            errors.append('Full name is required.')
        if not email or '@' not in email:
            errors.append('A valid email address is required.')
        if len(password) < 8:
            errors.append('Password must be at least 8 characters.')
        if password != confirm:
            errors.append('Passwords do not match.')
        if User.query.filter_by(email=email).first():
            errors.append('An account with that email already exists.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            # Re-render with previously entered values
            return render_template('auth/signup.html',
                                   full_name=full_name, email=email)

        # ── Create user ──────────────────────────────────────
        user = User(full_name=full_name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user, remember=False)
        flash(f'Welcome to FinTrack, {user.full_name.split()[0]}! 🎉', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('auth/signup.html')


# ─────────────────────────────────────────────────────────────
# Login
# ─────────────────────────────────────────────────────────────
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email     = request.form.get('email', '').strip().lower()
        password  = request.form.get('password', '')
        remember  = bool(request.form.get('remember'))
        role      = request.form.get('role', 'client')

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Invalid email or password. Please try again.', 'danger')
            return render_template('auth/login.html', email=email)

        # Role-based validation
        if role == 'admin' and not user.is_admin:
            flash('This account does not have administrative privileges.', 'danger')
            return render_template('auth/login.html', email=email)

        login_user(user, remember=remember)
        
        if user.is_admin:
            flash(f'Welcome Admin, {user.full_name.split()[0]}! 🛡️', 'success')
            return redirect(url_for('admin.clients'))

        flash(f'Welcome back, {user.full_name.split()[0]}!', 'success')

        # Honour the next parameter (safe redirect)
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        return redirect(url_for('dashboard.index'))

    return render_template('auth/login.html')


# ─────────────────────────────────────────────────────────────
# Logout
# ─────────────────────────────────────────────────────────────
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
