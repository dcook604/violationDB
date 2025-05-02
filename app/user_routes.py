from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from . import db
from .models import User, InvalidRoleError
from functools import wraps

user_api = Blueprint('user_api', __name__)

# Helper: admin_required for API

def admin_required_api(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# --- API endpoints will be added below ---

@user_api.route('/api/users', methods=['GET'])
@login_required
@admin_required_api
def api_list_users():
    users = User.query.all()
    return jsonify([
        {
            'id': u.id,
            'email': u.email,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'role': u.role,
            'is_active': u.is_active,
            'is_admin': u.is_admin
        } for u in users
    ])

@user_api.route('/api/users', methods=['POST'])
@login_required
@admin_required_api
def api_create_user():
    data = request.json or {}
    if not data.get('email') or not data.get('role'):
        return jsonify({'error': 'Email and role are required'}), 400
    try:
        # Use provided password if available, otherwise use default or generate
        if data.get('password'):
            password = data['password']
        else:
            password = User.generate_temp_password() if hasattr(User, 'generate_temp_password') else 'changeme123'
            
        user = User(
            email=data['email'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            password_hash=generate_password_hash(password),
            role=data['role'],
            is_active=data.get('is_active', True),
            is_admin=(data['role'] == 'admin')
        )
        db.session.add(user)
        db.session.commit()
        # Only return the password in the response if it was auto-generated
        result = {'message': 'User created', 'id': user.id}
        if not data.get('password'):
            result['temp_password'] = password
        return jsonify(result), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email address already registered'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_api.route('/api/users/<int:uid>', methods=['PUT'])
@login_required
@admin_required_api
def api_edit_user(uid):
    user = User.query.get_or_404(uid)
    data = request.json or {}
    user.email = data.get('email', user.email)
    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    if 'role' in data:
        user.role = data['role']
        user.is_admin = (data['role'] == 'admin')
    if 'is_active' in data:
        user.is_active = data['is_active']
    db.session.commit()
    return jsonify({'message': 'User updated'})

@user_api.route('/api/users/<int:uid>', methods=['DELETE'])
@login_required
@admin_required_api
def api_delete_user(uid):
    user = User.query.get_or_404(uid)
    if user.id == current_user.id:
        return jsonify({'error': 'You cannot delete your own account'}), 400
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'})

@user_api.route('/api/users/<int:uid>/change-password', methods=['POST'])
@login_required
def api_change_password(uid):
    if not (current_user.is_admin or current_user.id == uid):
        return jsonify({'error': 'Forbidden'}), 403
    user = User.query.get_or_404(uid)
    data = request.json or {}
    if not data.get('password'):
        return jsonify({'error': 'Password is required'}), 400
    user.set_password(data['password'])
    if hasattr(user, 'clear_temporary_password'):
        user.clear_temporary_password()
    db.session.commit()
    return jsonify({'message': 'Password changed'}) 