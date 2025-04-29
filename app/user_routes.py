from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from . import db
from .models import User, InvalidRoleError
from .forms import UserCreateForm, UserEditForm, UserPasswordChangeForm
from functools import wraps

bp = Blueprint('user_management', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to require admin privileges for a route
    
    Raises:
        403: If user is not authenticated or not an admin
    """
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
    """List all users in the system"""
    users = User.query.all()
    return render_template('user_management/list.html', users=users)

@bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def user_create():
    """Create a new user with temporary password"""
    form = UserCreateForm()
    if form.validate_on_submit():
        try:
            # Generate temporary password and create user
            temp_password = User.generate_temp_password()
            user = User(
                email=form.email.data,
                password_hash=generate_password_hash(temp_password),
                role=form.role.data,
                is_active=form.is_active.data,
                is_admin=(form.role.data == User.ROLE_ADMIN)
            )
            db.session.add(user)
            db.session.commit()
            
            flash(f'User created successfully. Temporary password: {temp_password}', 'success')
            return redirect(url_for('user_management.user_list'))
            
        except IntegrityError:
            db.session.rollback()
            flash('Email address already registered.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating user: {str(e)}', 'error')
    
    return render_template('user_management/create.html', form=form)

@bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def user_edit(id):
    """Edit user details and optionally reset password"""
    user = User.query.get_or_404(id)
    form = UserEditForm(obj=user)
    
    if form.validate_on_submit():
        try:
            # Update user details
            user.email = form.email.data
            user.set_role(form.role.data)
            user.is_active = form.is_active.data
            
            # Handle temporary password reset if requested
            if form.set_temporary_password.data:
                temp_password = user.set_temporary_password()
                flash(f'Temporary password set: {temp_password}', 'info')
            
            db.session.commit()
            flash('User updated successfully.', 'success')
            return redirect(url_for('user_management.user_list'))
            
        except InvalidRoleError as e:
            db.session.rollback()
            flash(str(e), 'error')
        except IntegrityError:
            db.session.rollback()
            flash('Email address already taken.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating user: {str(e)}', 'error')
    
    return render_template('user_management/edit.html', form=form, user=user)

@bp.route('/users/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def user_delete(id):
    """Delete a user account"""
    user = User.query.get_or_404(id)
    
    # Prevent self-deletion
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('user_management.user_list'))
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'error')
    
    return redirect(url_for('user_management.user_list'))

@bp.route('/users/<int:id>/change-password', methods=['GET', 'POST'])
@login_required
def user_change_password(id):
    """Change user password with proper authorization checks"""
    # Check authorization
    if not current_user.is_admin and current_user.id != id:
        flash('You can only change your own password.', 'error')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(id)
    form = UserPasswordChangeForm()
    
    if form.validate_on_submit():
        try:
            user.set_password(form.password.data)
            user.clear_temporary_password()
            flash('Password changed successfully.', 'success')
            return redirect(url_for('user_management.user_list' if current_user.is_admin else 'main.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error changing password: {str(e)}', 'error')
    
    return render_template('user_management/change_password.html', form=form, user=user) 