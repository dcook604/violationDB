from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, make_response, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, AccountLockedError, UserSession
from werkzeug.security import check_password_hash, generate_password_hash
from . import db
from functools import wraps
from datetime import datetime, timedelta
import logging
# --- Added for Password Reset --- 
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from flask import url_for
from .mail_utils import send_password_reset_email
# ------------------------------
from . import limiter # Import the limiter instance
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    get_jwt_identity, 
    get_jwt,
    jwt_required,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
    verify_jwt_in_request
)
from .jwt_config import get_jwt_identity_claims
from .jwt_auth import jwt_required_api

# Set up logger
logger = logging.getLogger(__name__)

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
                resp.headers['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept, Authorization, X-Requested-With, X-CSRF-TOKEN, X-CSRFToken, x-csrf-token, Expires, Cache-Control, Pragma'
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
        if get_jwt_identity():
            # Get origin for CORS
            origin = request.headers.get('Origin')
            allowed_origins = ['http://localhost:3001', 'http://localhost:3002', 'http://172.16.16.6:3001', 'http://172.16.16.6:5004', 'http://172.16.16.26', 'http://172.16.16.26:3001']
            
            # Include user details in response
            user_data = {
                'id': get_jwt_identity(),
                'email': get_jwt().get('email'),
                'first_name': get_jwt().get('first_name'),
                'last_name': get_jwt().get('last_name'),
                'role': get_jwt().get('role'),
                'is_admin': get_jwt().get('is_admin')
            }
            
            response = make_response(jsonify({'authenticated': True, 'user': user_data}))
            
            # Only set CORS headers for allowed origins
            if origin and origin in allowed_origins:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Credentials'] = 'true'
            
            # Update session activity if the function exists
            if hasattr(current_user, 'get_active_sessions'):
                # Get the session ID from the request
                session_token = request.cookies.get('session_token')
                if session_token:
                    # Find the session by token
                    from .models import UserSession
                    session = UserSession.query.filter_by(token=session_token, user_id=get_jwt_identity(), is_active=True).first()
                    if session and not session.is_expired():
                        session.update_activity()
            
            return response
        else:
            # User is not authenticated
            response = make_response(jsonify({'authenticated': False}))
            
            # Get origin for CORS
            origin = request.headers.get('Origin')
            allowed_origins = ['http://localhost:3001', 'http://localhost:3002', 'http://172.16.16.6:3001', 'http://172.16.16.6:5004', 'http://172.16.16.26', 'http://172.16.16.26:3001']
            
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
        allowed_origins = ['http://localhost:3001', 'http://localhost:3002', 'http://172.16.16.6:3001', 'http://172.16.16.6:5004', 'http://172.16.16.26', 'http://172.16.16.26:3001']
        
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
            logger.warning(f"Login attempt failed: Email or password missing. Email: {bool(email)}, Password: {bool(password)}")
            return jsonify({'error': 'Email and password are required'}), 400

        user = User.query.filter_by(email=email).first()
        
        if not user:
            logger.warning(f"Login attempt failed: User {email} not found.")
            # Return same error message to avoid user enumeration
            return jsonify({'error': 'Invalid credentials'}), 401

        if not user.password_hash:
            logger.warning(f"Login attempt failed: User {email} has no password hash set.")
            return jsonify({'error': 'Account not properly configured'}), 401

        # Check if account is locked
        if user.is_account_locked():
            lockout_time = user.account_locked_until
            logger.warning(f"Login attempt for locked account: {email}. Locked until {lockout_time}")
            return jsonify({'error': 'Account temporarily locked due to too many failed attempts. Please try again later.'}), 423
            
        try:
            # Verify the password
            if user.check_password(password):
                if not user.is_active:
                    logger.warning(f"Login attempt failed: User {email} is inactive.")
                    return jsonify({'error': 'Account pending approval'}), 403
                # Check if we need to migrate password to Argon2id
                if user.password_algorithm != 'argon2' or not user.password_hash.startswith('$argon2'):
                    user.migrate_to_argon2(password)
                    logger.info(f"Migrated password hash for user {email} to Argon2id")
                # Set session as permanent
                session.permanent = True
                # If configured to enforce single session, terminate other sessions
                if current_app.config.get('ENFORCE_SINGLE_SESSION', True):
                    user.terminate_all_sessions()
                    logger.info(f"Terminated existing sessions for user {email}")
                # Create a new session for this login
                user_session = user.create_session(
                    user_agent=request.headers.get('User-Agent'),
                    ip_address=request.remote_addr
                )
                logger.info(f"Created new session {user_session.id} for user {email}")
                # Explicitly login user
                login_user(user, remember=True)
                logger.info(f"User {email} logged in successfully.")
                # Update last login and reset failed attempts
                user.update_last_login()
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
                allowed_origins = ['http://localhost:3001', 'http://localhost:3002', 'http://172.16.16.6:3001', 'http://172.16.16.6:5004', 'http://172.16.16.26', 'http://172.16.16.26:3001']
                # Only set CORS headers for allowed origins
                if origin and origin in allowed_origins:
                    response.headers['Access-Control-Allow-Origin'] = origin
                    response.headers['Access-Control-Allow-Credentials'] = 'true'
                    # Set session token cookie 
                    response.set_cookie(
                        'session_token',
                        user_session.token,
                        httponly=True,  # Not accessible by JavaScript
                        secure=False,   # HTTP is ok for development
                        samesite='Lax', # Changed from config to direct value to ensure it works
                        domain=None,    # Allow the browser to determine the domain
                        path='/',
                        max_age=86400  # 24 hours in seconds
                    )
                # Manually set a test cookie for troubleshooting
                response.set_cookie(
                    'test_auth', 
                    'authenticated', 
                    httponly=False,
                    secure=False,
                    samesite='Lax',
                    domain=None,  # Allow the browser to determine the domain
                    path='/',
                    max_age=86400
                )
                # Print debug info about cookies being set
                logger.info(f"Setting session_token cookie: {user_session.token[:10]}... (truncated)")
                logger.info(f"Cookie parameters: domain=None, path=/, secure=False, samesite=Lax, httponly=True")
                logger.info(f"Response headers: {dict(response.headers)}")
                # Print debug info
                logger.debug("Response headers: %s", dict(response.headers))
                # Update login time and last activity
                session['login_time'] = datetime.utcnow().isoformat()
                session['last_activity'] = datetime.utcnow().isoformat()
                return response
            else:
                # Record the failed login attempt
                user.record_failed_login()
                # Get remaining attempts before lockout
                remaining_attempts = User.MAX_FAILED_ATTEMPTS - user.failed_login_attempts
                if remaining_attempts <= 0:
                    logger.warning(f"Account locked: User {email} exceeded maximum failed login attempts.")
                    return jsonify({'error': 'Account locked due to too many failed attempts. Please try again later.'}), 423
                elif remaining_attempts <= 3:
                    # Warn user about remaining attempts
                    logger.warning(f"Login attempt failed: Invalid password for user {email}. {remaining_attempts} attempts remaining.")
                    return jsonify({
                        'error': f'Invalid credentials. You have {remaining_attempts} attempts remaining before your account is temporarily locked.'
                    }), 401
                else:
                    logger.warning(f"Login attempt failed: Invalid password for user {email}.")
                return jsonify({'error': 'Invalid credentials'}), 401
                    
        except AccountLockedError as e:
            logger.warning(f"Login attempt on locked account: {email}. {str(e)}")
            return jsonify({'error': 'Account temporarily locked due to too many failed attempts. Please try again later.'}), 423
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Authentication error occurred'}), 500

@auth.route('/api/auth/logout', methods=['POST', 'OPTIONS'])
@cors_preflight
@jwt_required_api
def logout():
    if request.method == 'OPTIONS':
        return make_response()
    
    try:
        user_email = get_jwt().get('email')
        
        # Terminate the current session
        session_token = request.cookies.get('session_token')
        if session_token:
            user_session = UserSession.query.filter_by(token=session_token).first()
            if user_session:
                user_session.terminate()
        
        logout_user()
        session.clear()
        
        # Create response
        response = make_response(jsonify({'message': 'Logged out successfully'}))
        
        # Clear the session token cookie
        response.delete_cookie('session_token')
        response.delete_cookie('test_auth')
        
        logger.info(f"User {user_email} logged out successfully.")
        return response
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
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
    is_authenticated = get_jwt_identity()
    user_info = None
    
    if is_authenticated:
        user_info = {
            'id': get_jwt_identity(),
            'email': get_jwt().get('email'),
            'role': 'admin' if get_jwt().get('is_admin') else 'user'
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
    allowed_origins = ['http://localhost:3001', 'http://localhost:3002', 'http://172.16.16.6:3001', 'http://172.16.16.6:5004', 'http://172.16.16.26', 'http://172.16.16.26:3001']
    
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
    allowed_origins = ['http://localhost:3001', 'http://localhost:3002', 'http://172.16.16.6:3001', 'http://172.16.16.6:5004', 'http://172.16.16.26', 'http://172.16.16.26:3001']
    
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
    if get_jwt_identity():
        return jsonify({
            "user": {
                "id": get_jwt_identity(),
                "email": get_jwt().get('email'),
                "first_name": get_jwt().get('first_name'),
                "last_name": get_jwt().get('last_name'),
                "role": 'admin' if get_jwt().get('is_admin') else 'user',
                "is_admin": get_jwt().get('is_admin')
            }
        })
    else:
        return jsonify({"user": None}), 200

@auth.route('/api/auth/user-debug', methods=['GET'])
@jwt_required_api
def user_debug():
    """Debug endpoint to check current user details"""
    try:
        # Return detailed user information
        user_data = {
            'id': get_jwt_identity(),
            'email': get_jwt().get('email'),
            'first_name': get_jwt().get('first_name'),
            'last_name': get_jwt().get('last_name'),
            'is_admin': get_jwt().get('is_admin'),
            'role': get_jwt().get('role'),
            'is_active': get_jwt().get('is_active'),
            'is_authenticated': get_jwt_identity()
        }
        return jsonify({
            'user': user_data,
            'message': 'Debug information retrieved successfully'
        })
    except Exception as e:
        return jsonify({
            'error': f'Error retrieving debug information: {str(e)}'
        }), 500

@auth.route('/api/auth/unlock-account', methods=['POST', 'OPTIONS'])
@cors_preflight
@jwt_required_api
def unlock_account():
    """Admin endpoint to unlock a locked user account"""
    if request.method == 'OPTIONS':
        return make_response()
    
    # Verify admin permissions
    if not get_jwt().get('is_admin'):
        return jsonify({'error': 'Admin permissions required'}), 403
    
    try:
        data = request.get_json()
        if not data or 'user_id' not in data:
            return jsonify({'error': 'User ID is required'}), 400
            
        user_id = data['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        user.unlock_account()
        logger.info(f"Account unlocked: User {user.email} by admin {get_jwt().get('email')}")
        
        return jsonify({'message': f'Account for {user.email} has been unlocked successfully.'}), 200
        
    except Exception as e:
        logger.error(f"Error unlocking account: {str(e)}")
        return jsonify({'error': 'Failed to unlock account'}), 500

@auth.route('/api/auth/active-sessions', methods=['GET', 'OPTIONS'])
@cors_preflight
@jwt_required_api
def active_sessions():
    """Get list of active sessions for the current user"""
    if request.method == 'OPTIONS':
        return make_response()
    
    try:
        active_sessions = current_user.get_active_sessions()
        
        # Get current session token
        current_token = request.cookies.get('session_token')
        
        # Convert sessions to dictionary
        sessions_data = []
        for session in active_sessions:
            sessions_data.append({
                'id': session.id,
                'created_at': session.created_at.isoformat(),
                'last_activity': session.last_activity.isoformat(),
                'expires_at': session.expires_at.isoformat(),
                'user_agent': session.user_agent,
                'ip_address': session.ip_address,
                'is_current': session.token == current_token
            })
            
        return jsonify({
            'sessions': sessions_data,
            'count': len(sessions_data)
        })
    except Exception as e:
        logger.error(f"Error retrieving active sessions: {str(e)}")
        return jsonify({'error': 'Failed to retrieve sessions'}), 500

@auth.route('/api/auth/terminate-sessions', methods=['POST', 'OPTIONS'])
@cors_preflight
@jwt_required_api
def terminate_sessions():
    """Terminate all other sessions for the current user"""
    if request.method == 'OPTIONS':
        return make_response()
    
    try:
        current_token = request.cookies.get('session_token')
        if not current_token:
            return jsonify({'error': 'No active session found'}), 400
            
        # Find the current session
        current_session = UserSession.query.filter_by(token=current_token).first()
        if not current_session:
            return jsonify({'error': 'Current session not found'}), 400
            
        # Terminate all other sessions
        count = current_user.terminate_other_sessions(current_session.id)
        
        logger.info(f"User {get_jwt().get('email')} terminated {count} other sessions")
        return jsonify({
            'message': f'Successfully terminated {count} other sessions',
            'count': count
        })
    except Exception as e:
        logger.error(f"Error terminating sessions: {str(e)}")
        return jsonify({'error': 'Failed to terminate sessions'}), 500

@auth.route('/api/auth/terminate-session/<int:session_id>', methods=['POST', 'OPTIONS'])
@cors_preflight
@jwt_required_api
def terminate_specific_session(session_id):
    """Terminate a specific session"""
    if request.method == 'OPTIONS':
        return make_response()
    
    try:
        # Get current session token
        current_token = request.cookies.get('session_token')
        current_session = None
        if current_token:
            current_session = UserSession.query.filter_by(token=current_token).first()
        
        # Don't allow terminating the current session through this endpoint
        if current_session and current_session.id == session_id:
            return jsonify({'error': 'Cannot terminate current session. Use logout instead.'}), 400
            
        # Find the session to terminate
        session_to_terminate = UserSession.query.filter_by(
            id=session_id,
            user_id=get_jwt_identity(),
            is_active=True
        ).first()
        
        if not session_to_terminate:
            return jsonify({'error': 'Session not found or already terminated'}), 404
            
        # Terminate the session
        session_to_terminate.terminate()
        
        logger.info(f"User {get_jwt().get('email')} terminated session {session_id}")
        return jsonify({'message': 'Session terminated successfully'})
    except Exception as e:
        logger.error(f"Error terminating session {session_id}: {str(e)}")
        return jsonify({'error': 'Failed to terminate session'}), 500

@auth.route('/api/auth/register', methods=['POST', 'OPTIONS'])
@cors_preflight
def register_api():
    if request.method == 'OPTIONS':
        return make_response()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid data format'}), 400
        
        # Check required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            password_hash=generate_password_hash(data['password']),
            is_active=True,  # Auto-activate users
            role=User.ROLE_USER,  # Default to regular user role
            is_admin=False
        )
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"New user registered: {user.email}")
        
        # Log the user in
        login_user(user)
        
        # Create a new session
        if hasattr(user, 'create_session'):
            user_agent = request.headers.get('User-Agent')
            ip_address = request.remote_addr
            session = user.create_session(user_agent, ip_address)
            logger.info(f"Session created for new user: {session.token[:8]}...")
        
        # Update last login timestamp
        if hasattr(user, 'update_last_login'):
            user.update_last_login()
            logger.info(f"Last login updated for new user")
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'is_admin': user.is_admin
            }
        }), 201
    
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Registration failed'}), 500

# --- SESSION TIMEOUT HANDLING ---
@auth.before_app_request
def enforce_session_timeouts():
    # First, safely check if a JWT token exists
    try:
        verify_jwt_in_request(optional=True)
        # Only enforce for authenticated users
        if not get_jwt_identity():
            return
    except Exception:
        # If there's any issue with JWT verification, just return without action
        return
        
    now = datetime.utcnow()
    idle_timeout = current_app.config.get('IDLE_TIMEOUT_MINUTES', 30)
    absolute_timeout = current_app.config.get('PERMANENT_SESSION_LIFETIME', timedelta(hours=24))
    # Track login time and last activity in session
    login_time = session.get('login_time')
    last_activity = session.get('last_activity')
    # Set on first login
    if not login_time:
        session['login_time'] = now.isoformat()
        login_time = session['login_time']
    if not last_activity:
        session['last_activity'] = now.isoformat()
        last_activity = session['last_activity']
    # Parse times
    try:
        login_time_dt = datetime.fromisoformat(login_time)
        last_activity_dt = datetime.fromisoformat(last_activity)
    except Exception:
        # If parsing fails, force logout
        logout_user()
        session.clear()
        return redirect(url_for('auth.login_page'))
    # Check absolute timeout
    if now - login_time_dt > absolute_timeout:
        logout_user()
        session.clear()
        return redirect(url_for('auth.login_page'))
    # Check idle timeout
    if now - last_activity_dt > timedelta(minutes=idle_timeout):
        logout_user()
        session.clear()
        return redirect(url_for('auth.login_page'))
    # Update last activity
    session['last_activity'] = now.isoformat()

# --- RE-AUTHENTICATION FOR SENSITIVE ACTIONS ---
def require_recent_password(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Require password re-entry within the last 5 minutes
        from flask import session, request, jsonify
        from datetime import datetime, timedelta
        
        # First, safely check if a JWT token exists
        try:
            verify_jwt_in_request()
            if not get_jwt_identity():
                return jsonify({'error': 'Authentication required'}), 401
        except Exception:
            return jsonify({'error': 'Authentication required'}), 401
            
        pw_time = session.get('recent_password_time')
        now = datetime.utcnow()
        if not pw_time or (now - datetime.fromisoformat(pw_time)) > timedelta(minutes=5):
            return jsonify({'error': 'Re-authentication required', 'reauth': True}), 401
        return func(*args, **kwargs)
    return wrapper

# Example usage: apply to sensitive routes
# @auth.route('/api/auth/change-password', methods=['POST'])
# @login_required
# @require_recent_password
# def change_password():
#     ...

# In the password re-auth endpoint, after verifying password:
# session['recent_password_time'] = datetime.utcnow().isoformat()

# --- Authorization Decorators ---
def admin_required_api(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not get_jwt_identity():
            return jsonify({'error': 'Authentication required'}), 401
        if not get_jwt().get('is_admin'):
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# --- Password Reset --- 

def get_reset_serializer(secret_key=None, salt='password-reset-salt'):
    """Creates a timed serializer for password reset tokens."""
    if secret_key is None:
        secret_key = current_app.config['SECRET_KEY']
    return URLSafeTimedSerializer(secret_key, salt=salt)

@auth.route('/api/auth/request-password-reset', methods=['POST', 'OPTIONS'])
@cors_preflight
@limiter.limit("50 per hour; 10 per 5 minutes") # IP-based limit
@limiter.limit("3 per hour", key_func=lambda: request.get_json().get('email') if request.is_json else 'invalid_request') # Email-based limit
def request_password_reset():
    """Handles the request to send a password reset email."""
    if request.method == 'OPTIONS':
        return make_response()

    data = request.get_json()
    email = data.get('email', '').strip()

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    user = User.query.filter_by(email=email).first()

    # Security: Even if user not found, pretend to send email
    if user:
        s = get_reset_serializer()
        token = s.dumps({'user_id': user.id})

        # Construct frontend URL (Adjust logic based on deployment)
        # Determine if running in development or production based on config or env var
        is_development = current_app.config.get('DEBUG', False)
        
        # Base URL construction needs refinement for production vs dev
        # For now, attempt to guess based on request origin or config
        origin = request.headers.get('Origin')
        if origin:
            # Simple replacement (might break if backend/frontend ports differ significantly)
            # Assumes frontend runs on :3001 if origin includes a port
            if ':' in origin.split('//')[1]:
                 base_url_parts = origin.split(':')
                 base_url = f"{base_url_parts[0]}:{base_url_parts[1]}"
            else:
                 base_url = origin # No port specified in origin
        elif current_app.config.get('BASE_URL'):
            base_url = current_app.config['BASE_URL']
        else:
            # Fallback for local development if no origin/BASE_URL
            base_url = 'http://localhost:3001' # Default frontend dev URL

        # Ensure base_url ends with a slash
        if not base_url.endswith('/'):
            base_url += '/'

        reset_url = f"{base_url}reset-password/{token}" # Use frontend route
        logger.info(f"Generated password reset link for {email}: {reset_url}")

        # Send the email
        try:
            send_password_reset_email(user.email, reset_url)
        except Exception as e:
            # Log but don't expose failure to user
            logger.error(f"Exception while queueing/sending password reset email for {email}: {str(e)}")

    # Always return generic success to prevent user enumeration
    return jsonify({'message': 'If an account with that email exists, a password reset link has been sent.'}), 200


@auth.route('/api/auth/reset-password/<token>', methods=['POST', 'OPTIONS'])
@cors_preflight
def reset_password_with_token(token):
    """Handles the actual password reset using a token."""
    if request.method == 'OPTIONS':
        return make_response()

    data = request.get_json()
    new_password = data.get('password')

    if not new_password:
        return jsonify({'error': 'New password is required'}), 400

    s = get_reset_serializer()
    try:
        # Verify token signature and expiry (max_age = 24 hours = 86400 seconds)
        data = s.loads(token, max_age=86400)
        user_id = data.get('user_id')

        user = User.query.get(user_id)

        if not user:
             # This case could happen if the user was deleted after token generation
            logger.warning(f"Password reset attempt for non-existent user ID: {user_id} from token")
            return jsonify({'error': 'Invalid or expired token'}), 400 

        # Set the new password (using user.set_password handles hashing)
        user.set_password(new_password)
        # Clear any old temp password info just in case
        user.clear_temporary_password() 

        # Important: Invalidate all other sessions
        if hasattr(user, 'terminate_all_sessions'):
            count = user.terminate_all_sessions()
            logger.info(f"Terminated {count} sessions for user ID {user_id} after password reset.")
        else:
             logger.warning(f"User model does not have 'terminate_all_sessions' method.")

        db.session.commit()
        logger.info(f"Password successfully reset for user ID {user_id}")

        return jsonify({'message': 'Password reset successfully. Please log in with your new password.'}), 200

    except SignatureExpired:
        logger.warning(f"Password reset attempt with expired token: {token[:10]}...")
        return jsonify({'error': 'Password reset link has expired.'}), 400
    except BadTimeSignature as e:
        logger.warning(f"Password reset attempt with invalid token ({e}): {token[:10]}...")
        return jsonify({'error': 'Invalid password reset link.'}), 400
    except Exception as e:
        logger.error(f"Error during password reset with token: {str(e)}", exc_info=True)
        db.session.rollback() # Rollback in case of DB errors during commit
        return jsonify({'error': 'An error occurred during password reset.'}), 500
# --- End Password Reset ---

@auth.route('/api/auth/login-jwt', methods=['POST', 'OPTIONS'])
@cors_preflight
def login_jwt():
    """Login endpoint using JWT authentication
    
    Returns:
        JSON response with login status
    """
    if request.method == 'OPTIONS':
        return make_response()

    try:
        # Debug output for CSRF tracking
        logger.info("=== login-jwt endpoint called ===")
        logger.info(f"CSRF protection: WTF_CSRF_ENABLED={current_app.config.get('WTF_CSRF_ENABLED', 'Not set')}")
        logger.info(f"JWT_COOKIE_SAMESITE: {current_app.config.get('JWT_COOKIE_SAMESITE')}")
        logger.info(f"JWT_COOKIE_SECURE: {current_app.config.get('JWT_COOKIE_SECURE')}")
        logger.info(f"JWT_COOKIE_DOMAIN: {current_app.config.get('JWT_COOKIE_DOMAIN')}")
        logger.info(f"JWT_COOKIE_CSRF_PROTECT: {current_app.config.get('JWT_COOKIE_CSRF_PROTECT')}")
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Request cookies: {dict(request.cookies)}")
        logger.info(f"Request data: {request.data}")
        logger.info(f"Request form: {request.form}")
        
        # Extract request data with explicit error handling
        try:
            data = request.get_json()
            logger.info(f"Parsed JSON data: {data}")
        except Exception as e:
            logger.error(f"Failed to parse JSON data: {str(e)}")
            return jsonify({'error': 'Invalid JSON data'}), 400
        
        if not data:
            logger.error("No data provided in request")
            return jsonify({'error': 'No data provided'}), 400

        email = data.get('email', '').strip()
        password = data.get('password', '').strip()

        if not email or not password:
            logger.warning(f"Login attempt failed: Email or password missing. Email: {bool(email)}, Password: {bool(password)}")
            return jsonify({'error': 'Email and password are required'}), 400

        user = User.query.filter_by(email=email).first()
        
        if not user:
            logger.warning(f"Login attempt failed: User {email} not found.")
            # Return same error message to avoid user enumeration
            return jsonify({'error': 'Invalid credentials'}), 401

        if not user.password_hash:
            logger.warning(f"Login attempt failed: User {email} has no password hash set.")
            return jsonify({'error': 'Account not properly configured'}), 401

        # Check if account is locked
        if user.is_account_locked():
            lockout_time = user.account_locked_until
            logger.warning(f"Login attempt for locked account: {email}. Locked until {lockout_time}")
            return jsonify({'error': 'Account temporarily locked due to too many failed attempts. Please try again later.'}), 423
            
        try:
            # Verify the password
            if user.check_password(password):
                if not user.is_active:
                    logger.warning(f"Login attempt failed: User {email} is inactive.")
                    return jsonify({'error': 'Account pending approval'}), 403
                
                # Check if we need to migrate password to Argon2id
                if user.password_algorithm != 'argon2' or not user.password_hash.startswith('$argon2'):
                    user.migrate_to_argon2(password)
                    logger.info(f"Migrated password hash for user {email} to Argon2id")
                
                # Get identity and claims for the JWT
                identity, additional_claims = get_jwt_identity_claims(user)
                
                # Create tokens
                access_token = create_access_token(
                    identity=identity,
                    additional_claims=additional_claims
                )
                refresh_token = create_refresh_token(
                    identity=identity,
                    additional_claims=additional_claims
                )
                
                # Update last login and reset failed attempts
                user.update_last_login()
                
                # Create response with user data
                user_data = {
                    'id': user.id,
                    'email': user.email,
                    'role': 'admin' if user.is_admin else 'user',
                    'is_admin': user.is_admin
                }
                
                # Create a response object
                response = make_response(jsonify({
                    'login': True,
                    'user': user_data
                }))
                
                # Set JWT cookies
                set_access_cookies(response, access_token)
                set_refresh_cookies(response, refresh_token)
                
                # Get the origin from the request
                origin = request.headers.get('Origin')
                allowed_origins = ['http://localhost:3001', 'http://localhost:3002', 'http://172.16.16.6:3001', 'http://172.16.16.6:5004', 'http://172.16.16.26', 'http://172.16.16.26:3001']
                
                # Only set CORS headers for allowed origins
                if origin and origin in allowed_origins:
                    response.headers['Access-Control-Allow-Origin'] = origin
                    response.headers['Access-Control-Allow-Credentials'] = 'true'
                
                logger.info(f"JWT login successful for user {email}")
                logger.info(f"Response headers: {dict(response.headers)}")
                return response
            else:
                # Record the failed login attempt
                user.record_failed_login()
                # Get remaining attempts before lockout
                remaining_attempts = User.MAX_FAILED_ATTEMPTS - user.failed_login_attempts
                if remaining_attempts <= 0:
                    logger.warning(f"Account locked: User {email} exceeded maximum failed login attempts.")
                    return jsonify({'error': 'Account locked due to too many failed attempts. Please try again later.'}), 423
                elif remaining_attempts <= 3:
                    # Warn user about remaining attempts
                    logger.warning(f"Login attempt failed: Invalid password for user {email}. {remaining_attempts} attempts remaining.")
                    return jsonify({
                        'error': f'Invalid credentials. You have {remaining_attempts} attempts remaining before your account is temporarily locked.'
                    }), 401
                else:
                    logger.warning(f"Login attempt failed: Invalid password for user {email}.")
                return jsonify({'error': 'Invalid credentials'}), 401
                    
        except AccountLockedError as e:
            logger.warning(f"Login attempt on locked account: {email}. {str(e)}")
            return jsonify({'error': 'Account temporarily locked due to too many failed attempts. Please try again later.'}), 423
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Authentication error occurred'}), 500

@auth.route('/api/auth/logout-jwt', methods=['POST', 'OPTIONS'])
@cors_preflight
@jwt_required_api
def logout_jwt():
    """Logout endpoint for JWT authentication
    
    Returns:
        JSON response with logout status
    """
    if request.method == 'OPTIONS':
        return make_response()
    
    response = make_response(jsonify({'logout': True}))
    unset_jwt_cookies(response)
    
    # Get the origin from the request
    origin = request.headers.get('Origin')
    allowed_origins = ['http://localhost:3001', 'http://localhost:3002', 'http://172.16.16.6:3001', 'http://172.16.16.6:5004', 'http://172.16.16.26', 'http://172.16.16.26:3001']
    
    # Only set CORS headers for allowed origins
    if origin and origin in allowed_origins:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        
    return response

@auth.route('/api/auth/refresh-jwt', methods=['POST', 'OPTIONS'])
@cors_preflight
@jwt_required(refresh=True)
def refresh_jwt():
    """Refresh JWT token endpoint
    
    Returns:
        JSON response with new access token
    """
    if request.method == 'OPTIONS':
        return make_response()
    
    try:
        # Get identity from refresh token
        identity = get_jwt_identity()
        
        # Get claims from refresh token
        claims = get_jwt()
        
        # Create new access token
        access_token = create_access_token(
            identity=identity,
            additional_claims={
                'role': claims.get('role'),
                'is_admin': claims.get('is_admin'),
                'email': claims.get('email')
            }
        )
        
        # Create response
        response = make_response(jsonify({'refresh': True}))
        
        # Set new access token
        set_access_cookies(response, access_token)
        
        # Get the origin from the request
        origin = request.headers.get('Origin')
        allowed_origins = ['http://localhost:3001', 'http://localhost:3002', 'http://172.16.16.6:3001', 'http://172.16.16.6:5004', 'http://172.16.16.26', 'http://172.16.16.26:3001']
        
        # Only set CORS headers for allowed origins
        if origin and origin in allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            
        return response
    except Exception as e:
        logger.error(f"JWT refresh error: {str(e)}")
        return jsonify({'error': 'Refresh token invalid or expired'}), 401

@auth.route('/api/auth/status-jwt', methods=['GET', 'OPTIONS'])
@cors_preflight
@limiter.limit("200 per hour")  # Increased rate limit to 200 per hour from the default of 50
@jwt_required_api
def status_jwt():
    """Get authentication status using JWT
    
    Returns:
        JSON response with authentication status and user details
    """
    if request.method == 'OPTIONS':
        return make_response()
    
    # Get user claims from JWT
    claims = get_jwt()
    
    # Create user data from claims
    user_data = {
        'id': get_jwt_identity(),
        'email': claims.get('email'),
        'role': claims.get('role'),
        'is_admin': claims.get('is_admin')
    }
    
    # Create response
    response = make_response(jsonify({
        'authenticated': True,
        'user': user_data
    }))
    
    # Get the origin from the request
    origin = request.headers.get('Origin')
    allowed_origins = ['http://localhost:3001', 'http://localhost:3002', 'http://172.16.16.6:3001', 'http://172.16.16.6:5004', 'http://172.16.16.26', 'http://172.16.16.26:3001']
    
    # Only set CORS headers for allowed origins
    if origin and origin in allowed_origins:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        
    return response

@auth.route('/api/auth/test-login', methods=['POST', 'OPTIONS'])
@cors_preflight
def test_login():
    """Test login endpoint with no CSRF protection
    
    Returns:
        JSON response with login status
    """
    if request.method == 'OPTIONS':
        return make_response()

    try:
        # Debug output
        logger.info("=== test-login endpoint called ===")
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Request cookies: {dict(request.cookies)}")
        
        # Get JSON data
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        email = data.get('email', '').strip()
        password = data.get('password', '').strip()

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
            
        if not user.is_active:
            return jsonify({'error': 'Account pending approval'}), 403
        
        # Get identity and claims for the JWT
        identity, additional_claims = get_jwt_identity_claims(user)
        
        # Create tokens
        access_token = create_access_token(
            identity=identity,
            additional_claims=additional_claims
        )
        refresh_token = create_refresh_token(
            identity=identity,
            additional_claims=additional_claims
        )
        
        # Create response with user data
        user_data = {
            'id': user.id,
            'email': user.email,
            'role': 'admin' if user.is_admin else 'user',
            'is_admin': user.is_admin
        }
        
        # Create a response object
        response = make_response(jsonify({
            'login': True,
            'user': user_data
        }))
        
        # Set JWT cookies
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        
        # Set CORS headers
        origin = request.headers.get('Origin')
        allowed_origins = ['http://localhost:3001', 'http://localhost:3002', 'http://172.16.16.6:3001', 'http://172.16.16.6:5004', 'http://172.16.16.26', 'http://172.16.16.26:3001']
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            
        return response
            
    except Exception as e:
        logger.error(f"Test login error: {str(e)}")
        return jsonify({'error': 'Authentication error occurred'}), 500
