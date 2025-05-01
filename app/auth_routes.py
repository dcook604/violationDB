from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, make_response, session
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from werkzeug.security import check_password_hash, generate_password_hash
from . import db
from functools import wraps
from datetime import datetime

auth = Blueprint('auth', __name__)

def cors_preflight(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'OPTIONS':
            resp = make_response()
            origin = request.headers.get('Origin')
            if origin:  # Allow any origin in development
                resp.headers['Access-Control-Allow-Origin'] = origin
                resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
                resp.headers['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept, Authorization, X-Requested-With'
                resp.headers['Access-Control-Allow-Credentials'] = 'true'
                resp.headers['Access-Control-Max-Age'] = '1728000'
            return resp
        return f(*args, **kwargs)
    return decorated_function

@auth.route('/api/auth/session', methods=['GET', 'OPTIONS'])
@cors_preflight
def check_session():
    if request.method == 'OPTIONS':
        return make_response()
    
    try:
        # Debug logging
        print(f"Session check requested from {request.remote_addr}")
        print(f"Current user authenticated: {current_user.is_authenticated}")
        print(f"Request cookies: {request.cookies}")
        
        if current_user.is_authenticated:
            user_data = {
                'id': current_user.id,
                'email': current_user.email,
                'role': 'admin' if current_user.is_admin else 'user',
                'is_admin': current_user.is_admin  # Explicitly include is_admin boolean
            }
            
            # Create response with user data
            response = make_response(jsonify({'user': user_data}))
            
            # Get the origin from the request
            origin = request.headers.get('Origin')
            allowed_origins = ['http://localhost:3001', 'http://localhost:3002']
            
            # Only set CORS headers for allowed origins
            if origin and origin in allowed_origins:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                
            return response
        else:
            # Explicitly return a 401 with JSON when not authenticated
            print("User not authenticated, returning 401")
            
            # Create response with error message
            response = make_response(jsonify({'error': 'Unauthorized', 'user': None}), 401)
            
            # Get the origin from the request
            origin = request.headers.get('Origin')
            allowed_origins = ['http://localhost:3001', 'http://localhost:3002']
            
            # Only set CORS headers for allowed origins
            if origin and origin in allowed_origins:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                
            return response
    except Exception as e:
        print(f"Session check error: {str(e)}")
        
        # Create response with error message
        response = make_response(jsonify({'error': 'Session check failed'}), 500)
        
        # Get the origin from the request
        origin = request.headers.get('Origin')
        allowed_origins = ['http://localhost:3001', 'http://localhost:3002']
        
        # Only set CORS headers for allowed origins
        if origin and origin in allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            
        return response

@auth.route('/api/auth/login', methods=['POST', 'OPTIONS'])
@cors_preflight
def login():
    if request.method == 'OPTIONS':
        return make_response()

    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        email = data.get('email', '').strip()
        password = data.get('password', '').strip()

        if not email or not password:
            print(f"Login attempt failed: Email or password missing. Email: {bool(email)}, Password: {bool(password)}")
            return jsonify({'error': 'Email and password are required'}), 400

        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"Login attempt failed: User {email} not found.")
            return jsonify({'error': 'Invalid credentials'}), 401

        if not user.password_hash:
            print(f"Login attempt failed: User {email} has no password hash set.")
            return jsonify({'error': 'Account not properly configured'}), 401

        if check_password_hash(user.password_hash, password):
            if not user.is_active:
                print(f"Login attempt failed: User {email} is inactive.")
                return jsonify({'error': 'Account pending approval'}), 403
                
            # Set session as permanent
            session.permanent = True
            
            # Explicitly login user
            login_user(user, remember=True)
            print(f"User {email} logged in successfully.")
            
            # Create response with user data
            user_data = {
                'id': user.id,
                'email': user.email,
                'role': 'admin' if current_user.is_admin else 'user',
                'is_admin': current_user.is_admin  # Explicitly include is_admin boolean
            }
            
            # Create a response object with proper CORS headers for specific origin
            response = make_response(jsonify({'user': user_data}))
            
            # Get the origin from the request
            origin = request.headers.get('Origin')
            allowed_origins = ['http://localhost:3001', 'http://localhost:3002']
            
            # Only set CORS headers for allowed origins
            if origin and origin in allowed_origins:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Credentials'] = 'true'
            
            # Manually set a test cookie for troubleshooting
            response.set_cookie(
                'test_auth', 
                'authenticated', 
                httponly=False,
                secure=False,
                samesite='Lax',
                path='/',
                max_age=86400
            )
            
            # Print debug info
            print("Response headers:", dict(response.headers))
            
            return response
        else:
            print(f"Login attempt failed: Invalid password for user {email}.")
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        print(f"Login error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': 'Authentication error occurred'}), 500

@auth.route('/api/auth/logout', methods=['POST', 'OPTIONS'])
@cors_preflight
@login_required
def logout():
    if request.method == 'OPTIONS':
        return make_response()
    
    try:
        user_email = current_user.email
        logout_user()
        session.clear()
        print(f"User {user_email} logged out successfully.")
        return jsonify({'message': 'Logged out successfully'})
    except Exception as e:
        print(f"Logout error: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500

@auth.route('/login', methods=['GET'])
def login_page():
    return jsonify({'redirect': True, 'location': 'http://localhost:3001/login'}), 200

@auth.route('/register', methods=['GET'])
def register_redirect():
    return jsonify({'redirect': True, 'location': 'http://localhost:3001/register'}), 200

@auth.route('/reset-password', methods=['GET'])
def reset_password_redirect():
    return jsonify({'redirect': True, 'location': 'http://localhost:3001/reset-password'}), 200

@auth.route('/api/auth/test', methods=['GET', 'OPTIONS'])
@cors_preflight
def test_endpoint():
    if request.method == 'OPTIONS':
        return make_response()
    
    # No authentication required
    print("Test endpoint accessed")
    return jsonify({
        'message': 'Test endpoint successful',
        'headers': dict(request.headers),
        'cookies': dict(request.cookies)
    })

@auth.route('/api/auth/debug', methods=['GET', 'OPTIONS'])
@cors_preflight
def debug_session():
    if request.method == 'OPTIONS':
        return make_response()
    
    # No authentication check - just show the current session state
    is_authenticated = current_user.is_authenticated
    user_info = None
    
    if is_authenticated:
        user_info = {
            'id': current_user.id,
            'email': current_user.email,
            'role': 'admin' if current_user.is_admin else 'user'
        }
    
    # Check what cookies we're receiving
    cookies = dict(request.cookies)
    # Mask any sensitive values
    if 'session' in cookies:
        cookies['session'] = f"<masked {len(cookies['session'])} chars>"
    
    # Get session cookie settings
    from flask import current_app
    cookie_settings = {
        'name': current_app.config.get('SESSION_COOKIE_NAME'),
        'domain': current_app.config.get('SESSION_COOKIE_DOMAIN'),
        'path': current_app.config.get('SESSION_COOKIE_PATH'),
        'secure': current_app.config.get('SESSION_COOKIE_SECURE'),
        'httponly': current_app.config.get('SESSION_COOKIE_HTTPONLY'),
        'samesite': current_app.config.get('SESSION_COOKIE_SAMESITE')
    }
    
    result = {
        'authenticated': is_authenticated,
        'user': user_info,
        'request_cookies': cookies,
        'request_headers': dict(request.headers),
        'cookie_settings': cookie_settings
    }
    
    # Create response that doesn't depend on authentication
    response = make_response(jsonify(result))
    
    # Get the origin from the request
    origin = request.headers.get('Origin')
    allowed_origins = ['http://localhost:3001', 'http://localhost:3002']
    
    # Only set CORS headers for allowed origins
    if origin and origin in allowed_origins:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    
    return response

@auth.route('/api/auth/set-test-cookie', methods=['GET', 'OPTIONS'])
@cors_preflight
def set_test_cookie():
    if request.method == 'OPTIONS':
        return make_response()
    
    # Create response
    response = make_response(jsonify({
        'message': 'Test cookie set',
        'time': datetime.utcnow().isoformat()
    }))
    
    # Get the origin from the request
    origin = request.headers.get('Origin')
    allowed_origins = ['http://localhost:3001', 'http://localhost:3002']
    
    # Only set CORS headers for allowed origins
    if origin and origin in allowed_origins:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    
    # Set multiple test cookies with different configurations
    response.set_cookie(
        'test_cookie1', 
        'value1', 
        httponly=False,
        secure=False,
        samesite='Lax',
        path='/',
        max_age=86400
    )
    
    response.set_cookie(
        'test_cookie2', 
        'value2', 
        httponly=True,
        secure=False,
        samesite='Lax',
        path='/',
        max_age=86400
    )
    
    print("Test cookie response headers:", dict(response.headers))
    
    return response

@auth.route('/api/auth/session-alt')
def session_check():
    if current_user.is_authenticated:
        return jsonify({
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "role": 'admin' if current_user.is_admin else 'user',
                "is_admin": current_user.is_admin
            }
        })
    else:
        return jsonify({"user": None}), 200

@auth.route('/api/auth/user-debug', methods=['GET'])
@login_required
def user_debug():
    """Debug endpoint to check current user details"""
    try:
        # Return detailed user information
        user_data = {
            'id': current_user.id,
            'email': current_user.email,
            'is_admin': current_user.is_admin,
            'role': current_user.role,
            'is_active': current_user.is_active,
            'is_authenticated': current_user.is_authenticated
        }
        return jsonify({
            'user': user_data,
            'message': 'Debug information retrieved successfully'
        })
    except Exception as e:
        return jsonify({
            'error': f'Error retrieving debug information: {str(e)}'
        }), 500
