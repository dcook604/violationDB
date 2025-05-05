from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt, current_user

def jwt_required_api(fn):
    """Decorator to protect API routes with JWT
    
    Args:
        fn: The function to decorate
    
    Returns:
        decorated function
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({
                'error': 'Unauthorized',
                'message': str(e)
            }), 401
    return wrapper

def admin_required_api(fn):
    """Decorator to protect admin API routes with JWT
    
    Args:
        fn: The function to decorate
    
    Returns:
        decorated function
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            
            if claims.get('is_admin') == True:
                return fn(*args, **kwargs)
            else:
                return jsonify({
                    'error': 'Forbidden',
                    'message': 'Admin privileges required'
                }), 403
        except Exception as e:
            return jsonify({
                'error': 'Unauthorized',
                'message': str(e)
            }), 401
    return wrapper

def role_required_api(*roles):
    """Decorator to protect API routes with specific roles
    
    Args:
        *roles: List of allowed roles
    
    Returns:
        decorator function
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                
                if claims.get('role') in roles or claims.get('is_admin') == True:
                    return fn(*args, **kwargs)
                else:
                    return jsonify({
                        'error': 'Forbidden',
                        'message': f'Required role not found. Must be one of: {", ".join(roles)}'
                    }), 403
            except Exception as e:
                return jsonify({
                    'error': 'Unauthorized',
                    'message': str(e)
                }), 401
        return wrapper
    return decorator 