from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token
from datetime import timedelta
import secrets
import os

# JWT default configuration
# These should ultimately be moved to environment variables or a secure config file
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or secrets.token_hex(32)
JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)  # 30 minutes
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)  # 7 days
JWT_COOKIE_SECURE = False  # Set to True in production (HTTPS only)
JWT_COOKIE_HTTPONLY = True  # Not accessible by JavaScript
JWT_COOKIE_SAMESITE = 'Lax'  # Prevents CSRF attacks

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
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_CSRF_METHODS'] = ['POST', 'PUT', 'PATCH', 'DELETE']
    app.config['JWT_CSRF_IN_COOKIES'] = True
    
    # Initialize JWT manager
    jwt = JWTManager(app)
    
    # Custom callbacks can be registered here
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        """Convert user model to JWT identity
        
        Args:
            user: User object
        
        Returns:
            int: User ID
        """
        if isinstance(user, dict):
            return user.get('id')
        return user.id

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
        user = User.query.filter_by(id=identity).first()
        return user
    
    return jwt

def get_jwt_identity_claims(user):
    """Generate JWT identity and claims
    
    Args:
        user: User object
    
    Returns:
        tuple: (identity, claims)
    """
    identity = user.id
    claims = {
        'role': user.role,
        'is_admin': user.is_admin,
        'email': user.email
    }
    
    return identity, claims 