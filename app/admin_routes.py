from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import User
from . import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/users')
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('Admins only.', 'danger')
        return redirect(url_for('main.dashboard'))
    users = User.query.order_by(User.email).all()
    return render_template('manage_users.html', users=users)

@admin_bp.route('/admin/users/<int:uid>/promote', methods=['POST'])
@login_required
def promote_user(uid):
    if not current_user.is_admin:
        flash('Admins only.', 'danger')
        return redirect(url_for('main.dashboard'))
    user = User.query.get_or_404(uid)
    user.is_admin = True
    db.session.commit()
    flash(f'User {user.email} promoted to admin.', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/admin/users/<int:uid>/demote', methods=['POST'])
@login_required
def demote_user(uid):
    if not current_user.is_admin:
        flash('Admins only.', 'danger')
        return redirect(url_for('main.dashboard'))
    user = User.query.get_or_404(uid)
    user.is_admin = False
    db.session.commit()
    flash(f'User {user.email} demoted from admin.', 'success')
    return redirect(url_for('admin.manage_users'))
