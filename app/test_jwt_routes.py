from flask import Blueprint, jsonify
from .jwt_auth import jwt_required_api, admin_required_api, role_required_api
from flask_jwt_extended import get_jwt_identity, get_jwt

test_jwt_bp = Blueprint('test_jwt', __name__)

@test_jwt_bp.route('/api/test/jwt', methods=['GET'])
@jwt_required_api
def test_jwt():
    """Test endpoint to verify JWT authentication
    
    Returns:
        JSON response with user identity and claims
    """
    identity = get_jwt_identity()
    claims = get_jwt()
    
    return jsonify({
        'message': 'JWT authentication successful',
        'identity': identity,
        'claims': claims
    })

@test_jwt_bp.route('/api/test/jwt/admin', methods=['GET'])
@admin_required_api
def test_jwt_admin():
    """Test endpoint to verify JWT admin authentication
    
    Returns:
        JSON response for admin-only access
    """
    identity = get_jwt_identity()
    claims = get_jwt()
    
    return jsonify({
        'message': 'JWT admin authentication successful',
        'identity': identity,
        'claims': claims
    })

@test_jwt_bp.route('/api/test/jwt/role/<role>', methods=['GET'])
@role_required_api('admin', 'manager')
def test_jwt_role(role):
    """Test endpoint to verify JWT role authentication
    
    Args:
        role: The role to test for
    
    Returns:
        JSON response for role-based access
    """
    identity = get_jwt_identity()
    claims = get_jwt()
    
    return jsonify({
        'message': f'JWT role authentication successful for role: {role}',
        'identity': identity,
        'claims': claims
    }) 