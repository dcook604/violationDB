from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token
from datetime import timedelta
import secrets
import os

# JWT default configuration
# These should ultimately be moved to environment variables or a secure config file
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or secrets.token_hex(32)
JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)  # 30 minutes default
JWT_EXTENDED_ACCESS_TOKEN_EXPIRES = timedelta(hours=6)  # 6 hours for "Remember Me"
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)  # 7 days default
JWT_EXTENDED_REFRESH_TOKEN_EXPIRES = timedelta(days=30)  # 30 days for "Remember Me"

# Set Secure flag based on environment
if os.environ.get('FLASK_ENV') == 'production':
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_SAMESITE = 'Lax'  # Prevents CSRF attacks in production
else:
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_SAMESITE = None  # None is more compatible for cross-origin in development

JWT_COOKIE_HTTPONLY = True  # Not accessible by JavaScript
JWT_COOKIE_DOMAIN = None  # Let the browser determine the domain

def init_jwt(app):
    """Initialize JWT with the Flask app
    
    Args:
        app: Flask application instance
    
    Returns:
        JWTManager: The initialized JWT manager
    """
    # Configure JWT settings
    app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = JWT_ACCESS_TOKEN_EXPIRES
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = JWT_REFRESH_TOKEN_EXPIRES
    app.config['JWT_COOKIE_SECURE'] = JWT_COOKIE_SECURE
    app.config['JWT_COOKIE_HTTPONLY'] = JWT_COOKIE_HTTPONLY
    app.config['JWT_COOKIE_SAMESITE'] = JWT_COOKIE_SAMESITE
    app.config['JWT_COOKIE_DOMAIN'] = JWT_COOKIE_DOMAIN
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # Disable CSRF protection for cookies
    
    # Log JWT configuration for debugging
    app.logger.info("JWT Configuration:")
    app.logger.info(f"  JWT_COOKIE_SECURE: {JWT_COOKIE_SECURE}")
    app.logger.info(f"  JWT_COOKIE_HTTPONLY: {JWT_COOKIE_HTTPONLY}")
    app.logger.info(f"  JWT_COOKIE_SAMESITE: {JWT_COOKIE_SAMESITE}")
    app.logger.info(f"  JWT_COOKIE_DOMAIN: {JWT_COOKIE_DOMAIN}")
    app.logger.info(f"  JWT_COOKIE_CSRF_PROTECT: {app.config['JWT_COOKIE_CSRF_PROTECT']}")
    app.logger.info(f"  JWT_TOKEN_LOCATION: {app.config['JWT_TOKEN_LOCATION']}")
    
    # Initialize JWT manager
    jwt = JWTManager(app)
    
    # Custom callbacks can be registered here
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        """Convert user model or id to JWT identity
        Args:
            user: User object, dict, or int/str
        Returns:
            str: User ID or identity as string
        """
        if isinstance(user, dict):
            return str(user.get('id'))
        if hasattr(user, 'id'):
            return str(user.id)
        return str(user)  # ensure always a string

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """Load user based on JWT identity
        
        Args:
            _jwt_header: JWT header
            jwt_data: JWT data
        
        Returns:
            User: User object or None
        """
        from .models import User
        identity = jwt_data["sub"]
        return User.query.get(identity)
    
    # Debug logging for the most common JWT errors
    @jwt.expired_token_loader
    def expired_token_callback(_jwt_header, jwt_data):
        app.logger.warning(f"Expired token: {jwt_data}")
        return {'error': 'Token has expired'}, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        app.logger.warning(f"Invalid token: {reason}")
        return {'error': f'Invalid token: {reason}'}, 401
    
    @jwt.unauthorized_loader
    def unauthorized_callback(reason):
        app.logger.warning(f"Missing token: {reason}")
        return {'error': 'Missing authorization token'}, 401
    
    return jwt

def get_jwt_identity_claims(user):
    """Generate JWT identity and claims
    
    Args:
        user: User object
    
    Returns:
        tuple: (identity, claims)
    """
    identity = str(user.id)  # Ensure identity is always a string
    claims = {
        'role': user.role,
        'is_admin': user.is_admin,
        'email': user.email
    }
    
    return identity, claims

def get_token_expiration(remember=False):
    """Get token expiration times based on remember me setting
    
    Args:
        remember: Whether to use extended expiration times
    
    Returns:
        tuple: (access_expires, refresh_expires)
    """
    if remember:
        return JWT_EXTENDED_ACCESS_TOKEN_EXPIRES, JWT_EXTENDED_REFRESH_TOKEN_EXPIRES
    return JWT_ACCESS_TOKEN_EXPIRES, JWT_REFRESH_TOKEN_EXPIRES 