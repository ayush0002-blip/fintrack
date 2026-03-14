from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.forms import ProfileForm, ChangePasswordForm

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    profile_form = ProfileForm(obj=current_user)
    password_form = ChangePasswordForm()

    # Determine which form was submitted
    if 'full_name' in request.form:
        if profile_form.validate_on_submit():
            current_user.full_name = profile_form.full_name.data
            current_user.email = profile_form.email.data
            db.session.commit()
            flash('Your profile has been updated.', 'success')
            return redirect(url_for('settings.index'))
    
    elif 'current_password' in request.form:
        if password_form.validate_on_submit():
            if current_user.check_password(password_form.current_password.data):
                current_user.set_password(password_form.new_password.data)
                db.session.commit()
                flash('Your password has been changed.', 'success')
                return redirect(url_for('settings.index'))
            else:
                flash('Invalid current password.', 'danger')

    return render_template(
        'settings.html',
        profile_form=profile_form,
        password_form=password_form
    )
