from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from . import db
from .models import User, InvalidRoleError
from functools import wraps
from flask_jwt_extended import get_jwt, get_jwt_identity
from app.jwt_auth import jwt_required_api

user_api = Blueprint('user_api', __name__)

# Helper: admin_required for API

def admin_required_api(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        claims = get_jwt()
        is_admin = claims.get('is_admin')
        user_id = get_jwt_identity()
        if not is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# --- API endpoints will be added below ---

@user_api.route('/api/users', methods=['GET'])
@admin_required_api
def api_list_users():
    MAX_PAGE_SIZE = 100
    try:
        page = int(request.args.get('page', 1))
    except Exception:
        return jsonify({'error': 'Invalid page parameter'}), 400
    try:
        per_page = int(request.args.get('per_page', 10))
    except Exception:
        return jsonify({'error': 'Invalid per_page parameter'}), 400
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 10
    if per_page > MAX_PAGE_SIZE:
        return jsonify({'error': f'Maximum per_page is {MAX_PAGE_SIZE}'}), 400
    users_query = User.query.order_by(User.id)
    pagination = users_query.paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items
    return jsonify({
        'users': [
            {
                'id': u.id,
                'email': u.email,
                'first_name': u.first_name,
                'last_name': u.last_name,
                'position': u.position,
                'role': u.role,
                'is_active': u.is_active,
                'is_admin': u.is_admin
            } for u in users
        ],
        'pagination': {
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    })

@user_api.route('/api/users', methods=['POST'])
@admin_required_api
def api_create_user():
    data = request.json or {}
    required_fields = ['email', 'role', 'first_name', 'last_name', 'position']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field.replace("_", " ").title()} is required'}), 400
    valid_positions = ['Council', 'Property Manager', 'Caretaker', 'Cleaner', 'Concierge']
    if data['position'] not in valid_positions:
        return jsonify({'error': 'Invalid position'}), 400
    try:
        # Use provided password if available, otherwise use default or generate
        if data.get('password'):
            password = data['password']
        else:
            password = User.generate_temp_password() if hasattr(User, 'generate_temp_password') else 'changeme123'
        user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            position=data['position'],
            password_hash=generate_password_hash(password),
            role=data['role'],
            is_active=data.get('is_active', True),
            is_admin=(data['role'] == 'admin')
        )
        db.session.add(user)
        db.session.commit()
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
@admin_required_api
def api_edit_user(uid):
    user = User.query.get_or_404(uid)
    data = request.json or {}
    if 'email' in data:
        user.email = data['email']
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'position' in data:
        valid_positions = ['Council', 'Property Manager', 'Caretaker', 'Cleaner', 'Concierge']
        if data['position'] not in valid_positions:
            return jsonify({'error': 'Invalid position'}), 400
        user.position = data['position']
    if 'role' in data:
        user.role = data['role']
        user.is_admin = (data['role'] == 'admin')
    if 'is_active' in data:
        user.is_active = data['is_active']
    db.session.commit()
    return jsonify({'message': 'User updated'})

@user_api.route('/api/users/<int:uid>', methods=['DELETE'])
@admin_required_api
def api_delete_user(uid):
    user = User.query.get_or_404(uid)
    if user.id == current_user.id:
        return jsonify({'error': 'You cannot delete your own account'}), 400
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'})

@user_api.route('/api/users/<int:uid>/change-password', methods=['POST'])
def api_change_password(uid):
    claims = get_jwt()
    is_admin = claims.get('is_admin')
    user_id = get_jwt_identity()
    if not (is_admin or user_id == uid):
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