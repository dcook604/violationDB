from flask import Blueprint, jsonify
from flask_wtf.csrf import generate_csrf

csrf_bp = Blueprint('csrf', __name__)

@csrf_bp.route('/api/csrf-token', methods=['GET'])
def get_csrf_token():
    """Get a CSRF token to be used for requests
    
    Returns:
        JSON response with CSRF token
    """
    token = generate_csrf()
    return jsonify({
        'token': token
    }) 