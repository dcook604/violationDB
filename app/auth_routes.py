from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, make_response, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, AccountLockedError, UserSession
from werkzeug.security import check_password_hash, generate_password_hash
from . import db
from functools import wraps
from datetime import datetime, timedelta
import logging

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
        print(f"Request headers: {dict(request.headers)}")
        print(f"Origin: {request.headers.get('Origin')}")
        
        # Check for session token specifically and log it
        session_token = request.cookies.get('session_token')
        print(f"Session token present: {bool(session_token)}")
        if session_token:
            print(f"Session token value (truncated): {session_token[:10]}...")
        
        if current_user.is_authenticated:
            # Check for session token in request
            session_token = request.cookies.get('session_token')
            
            if session_token:
                # Find the session
                user_session = UserSession.query.filter_by(
                    token=session_token,
                    is_active=True
                ).first()
                
                # If session exists, check if it's expired
                if user_session:
                    print(f"Found active session for token, user_id={user_session.user_id}")
                    # Check for absolute timeout (24 hours)
                    if user_session.is_expired():
                        # Session has expired, force logout
                        logout_user()
                        session.clear()
                        print(f"Session expired for user {current_user.email}")
                        return jsonify({'error': 'Session expired', 'user': None}), 401
                    
                    # Check for idle timeout (30 minutes)
                    if user_session.is_idle_timeout():
                        # Session is idle, force logout
                        logout_user()
                        session.clear()
                        user_session.terminate()
                        print(f"Session idle timeout for user {current_user.email}")
                        return jsonify({'error': 'Session timeout due to inactivity', 'user': None}), 401
                    
                    # Session is valid, update activity
                    user_session.update_activity()
                    print(f"Updated session activity timestamp")
                else:
                    # Session token not found or not active
                    print(f"Session token not found or not active: {session_token[:10]}...")
                    logout_user()
                    session.clear()
                    print(f"Invalid session token for user {current_user.email}")
                    return jsonify({'error': 'Invalid session', 'user': None}), 401
            
            user_data = {
                'id': current_user.id,
                'email': current_user.email,
                'role': 'admin' if current_user.is_admin else 'user',
                'is_admin': current_user.is_admin  # Explicitly include is_admin boolean
            }
            
            # Create response with user data
            response = make_response(jsonify({'user': user_data}))
            print(f"Creating successful session response for user {current_user.email}")
            
            # Get the origin from the request
            origin = request.headers.get('Origin')
            allowed_origins = ['http://localhost:3001', 'http://localhost:3002', 'http://172.16.16.6:3001', 'http://172.16.16.6:5004']
            
            # Only set CORS headers for allowed origins
            if origin and origin in allowed_origins:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                print(f"Added CORS headers for origin: {origin}")
                
            return response
        else:
            # Explicitly return a 401 with JSON when not authenticated
            print("User not authenticated, returning 401")
            
            # Create response with error message
            response = make_response(jsonify({'error': 'Unauthorized', 'user': None}), 401)
            
            # Get the origin from the request
            origin = request.headers.get('Origin')
            allowed_origins = ['http://localhost:3001', 'http://localhost:3002', 'http://172.16.16.6:3001', 'http://172.16.16.6:5004']
            
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
        allowed_origins = ['http://localhost:3001', 'http://localhost:3002', 'http://172.16.16.6:3001', 'http://172.16.16.6:5004']
        
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
                allowed_origins = ['http://localhost:3001', 'http://localhost:3002', 'http://172.16.16.6:3001', 'http://172.16.16.6:5004']
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
@login_required
def logout():
    if request.method == 'OPTIONS':
        return make_response()
    
    try:
        user_email = current_user.email
        
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
    allowed_origins = ['http://localhost:3001', 'http://localhost:3002', 'http://172.16.16.6:3001', 'http://172.16.16.6:5004']
    
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
    allowed_origins = ['http://localhost:3001', 'http://localhost:3002', 'http://172.16.16.6:3001', 'http://172.16.16.6:5004']
    
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

@auth.route('/api/auth/unlock-account', methods=['POST', 'OPTIONS'])
@cors_preflight
@login_required
def unlock_account():
    """Admin endpoint to unlock a locked user account"""
    if request.method == 'OPTIONS':
        return make_response()
    
    # Verify admin permissions
    if not current_user.is_admin:
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
        logger.info(f"Account unlocked: User {user.email} by admin {current_user.email}")
        
        return jsonify({'message': f'Account for {user.email} has been unlocked successfully.'}), 200
        
    except Exception as e:
        logger.error(f"Error unlocking account: {str(e)}")
        return jsonify({'error': 'Failed to unlock account'}), 500

@auth.route('/api/auth/active-sessions', methods=['GET', 'OPTIONS'])
@cors_preflight
@login_required
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
@login_required
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
        
        logger.info(f"User {current_user.email} terminated {count} other sessions")
        return jsonify({
            'message': f'Successfully terminated {count} other sessions',
            'count': count
        })
    except Exception as e:
        logger.error(f"Error terminating sessions: {str(e)}")
        return jsonify({'error': 'Failed to terminate sessions'}), 500

@auth.route('/api/auth/terminate-session/<int:session_id>', methods=['POST', 'OPTIONS'])
@cors_preflight
@login_required
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
            user_id=current_user.id,
            is_active=True
        ).first()
        
        if not session_to_terminate:
            return jsonify({'error': 'Session not found or already terminated'}), 404
            
        # Terminate the session
        session_to_terminate.terminate()
        
        logger.info(f"User {current_user.email} terminated session {session_id}")
        return jsonify({'message': 'Session terminated successfully'})
    except Exception as e:
        logger.error(f"Error terminating session {session_id}: {str(e)}")
        return jsonify({'error': 'Failed to terminate session'}), 500
