from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from . import db
from .models import User
from .forms import UserCreateForm, UserEditForm, UserPasswordChangeForm
from functools import wraps

bp = Blueprint('user_management', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need to be an admin to access this page.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/users')
@login_required
@admin_required
def user_list():
    users = User.query.all()
    return render_template('user_management/list.html', users=users)

@bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def user_create():
    form = UserCreateForm()
    if form.validate_on_submit():
        # Generate a temporary password
        temp_password = User.generate_temp_password()
        user = User(
            email=form.email.data,
            password_hash=generate_password_hash(temp_password),
            role=form.role.data,
            is_active=form.is_active.data,
            is_admin=(form.role.data == 'admin')
        )
        db.session.add(user)
        db.session.commit()
        
        # Set temporary password
        user.set_temporary_password()
        
        flash(f'User created successfully. Temporary password: {temp_password}', 'success')
        return redirect(url_for('user_management.user_list'))
    
    return render_template('user_management/create.html', form=form)

@bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def user_edit(id):
    user = User.query.get_or_404(id)
    form = UserEditForm(obj=user)
    
    if form.validate_on_submit():
        user.email = form.email.data
        user.role = form.role.data
        user.is_active = form.is_active.data
        user.is_admin = (form.role.data == 'admin')
        
        if form.set_temporary_password.data:
            temp_password = user.set_temporary_password()
            flash(f'Temporary password set: {temp_password}', 'info')
        
        db.session.commit()
        flash('User updated successfully.', 'success')
        return redirect(url_for('user_management.user_list'))
    
    return render_template('user_management/edit.html', form=form, user=user)

@bp.route('/users/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def user_delete(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('user_management.user_list'))
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('user_management.user_list'))

@bp.route('/users/<int:id>/change-password', methods=['GET', 'POST'])
@login_required
def user_change_password(id):
    if not current_user.is_admin and current_user.id != id:
        flash('You can only change your own password.', 'error')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(id)
    form = UserPasswordChangeForm()
    
    if form.validate_on_submit():
        user.password_hash = generate_password_hash(form.password.data)
        user.clear_temporary_password()  # Clear any temporary password
        db.session.commit()
        flash('Password changed successfully.', 'success')
        return redirect(url_for('user_management.user_list' if current_user.is_admin else 'main.index'))
    
    return render_template('user_management/change_password.html', form=form, user=user) 