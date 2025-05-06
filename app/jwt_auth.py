from functools import wraps
from flask import jsonify, request, make_response
from flask_jwt_extended import verify_jwt_in_request, get_jwt, current_user
import logging

# Set up logger
logger = logging.getLogger(__name__)

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
            logger.error(f"JWT authentication error: {str(e)}")
            
            # Get the origin from the request
            origin = request.headers.get('Origin')
            allowed_origins = ['http://localhost:3001', 'http://localhost:3002', 'http://172.16.16.6:3001', 'http://172.16.16.6:5004', 'http://172.16.16.26', 'http://172.16.16.26:3001']
            
            # Create response with error
            response = make_response(jsonify({
                'error': 'Unauthorized',
                'message': str(e)
            }), 401)
            
            # Only set CORS headers for allowed origins
            if origin and origin in allowed_origins:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                
            return response
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
                # Get the origin from the request
                origin = request.headers.get('Origin')
                allowed_origins = ['http://localhost:3001', 'http://localhost:3002', 'http://172.16.16.6:3001', 'http://172.16.16.6:5004', 'http://172.16.16.26', 'http://172.16.16.26:3001']
                
                # Create response with error
                response = make_response(jsonify({
                    'error': 'Forbidden',
                    'message': 'Admin privileges required'
                }), 403)
                
                # Only set CORS headers for allowed origins
                if origin and origin in allowed_origins:
                    response.headers['Access-Control-Allow-Origin'] = origin
                    response.headers['Access-Control-Allow-Credentials'] = 'true'
                    
                return response
        except Exception as e:
            logger.error(f"JWT admin authentication error: {str(e)}")
            
            # Get the origin from the request
            origin = request.headers.get('Origin')
            allowed_origins = ['http://localhost:3001', 'http://localhost:3002', 'http://172.16.16.6:3001', 'http://172.16.16.6:5004', 'http://172.16.16.26', 'http://172.16.16.26:3001']
            
            # Create response with error
            response = make_response(jsonify({
                'error': 'Unauthorized',
                'message': str(e)
            }), 401)
            
            # Only set CORS headers for allowed origins
            if origin and origin in allowed_origins:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                
            return response
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
                    # Get the origin from the request
                    origin = request.headers.get('Origin')
                    allowed_origins = ['http://localhost:3001', 'http://localhost:3002', 'http://172.16.16.6:3001', 'http://172.16.16.6:5004', 'http://172.16.16.26', 'http://172.16.16.26:3001']
                    
                    # Create response with error
                    response = make_response(jsonify({
                        'error': 'Forbidden',
                        'message': f'Required role not found. Must be one of: {", ".join(roles)}'
                    }), 403)
                    
                    # Only set CORS headers for allowed origins
                    if origin and origin in allowed_origins:
                        response.headers['Access-Control-Allow-Origin'] = origin
                        response.headers['Access-Control-Allow-Credentials'] = 'true'
                        
                    return response
            except Exception as e:
                logger.error(f"JWT role authentication error: {str(e)}")
                
                # Get the origin from the request
                origin = request.headers.get('Origin')
                allowed_origins = ['http://localhost:3001', 'http://localhost:3002', 'http://172.16.16.6:3001', 'http://172.16.16.6:5004', 'http://172.16.16.26', 'http://172.16.16.26:3001']
                
                # Create response with error
                response = make_response(jsonify({
                    'error': 'Unauthorized',
                    'message': str(e)
                }), 401)
                
                # Only set CORS headers for allowed origins
                if origin and origin in allowed_origins:
                    response.headers['Access-Control-Allow-Origin'] = origin
                    response.headers['Access-Control-Allow-Credentials'] = 'true'
                    
                return response
        return wrapper
    return decorator 