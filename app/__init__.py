import os
import logging
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_cors import CORS
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .config import config_by_name
from datetime import timedelta
from flask.sessions import SecureCookieSessionInterface
import os.path
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

# Initialize Sentry
def init_sentry(app):
    sentry_dsn = app.config.get('SENTRY_DSN')
    environment = app.config.get('FLASK_ENV', 'development')
    
    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[FlaskIntegration()],
            environment=environment,
            
            # Set traces_sample_rate to 1.0 to capture 100% of transactions for performance monitoring
            # We recommend adjusting this value in production
            traces_sample_rate=1.0,
            
            # By default the SDK will try to use the SENTRY_RELEASE
            # environment variable, or infer a git commit
            # release=os.environ.get("SENTRY_RELEASE"),
            
            # Enable performance monitoring
            enable_tracing=True,
            
            # Send IP address with errors
            send_default_pii=True,
        )
        app.logger.info(f"Sentry initialized in {environment} mode")
    else:
        app.logger.warning("Sentry DSN not found. Sentry integration disabled.")

# Custom session interface to fix SameSite issue
class CustomSessionInterface(SecureCookieSessionInterface):
    def get_cookie_samesite(self, app):
        # Use SameSite=Strict in production if possible, else Lax
        return 'Strict' if app.config.get('SESSION_COOKIE_SECURE') else 'Lax'

# Configure logging to save errors to flask_error.log
logging.basicConfig(
    filename='flask_error.log',
    level=logging.INFO,  # Change from ERROR to INFO to capture more detailed logs
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)

# Create a console handler to also show logs in the terminal
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per day", "200 per hour"],
    storage_uri="memory://",
    strategy="fixed-window"
)

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))

# Add custom unauthorized handler for API requests
@login_manager.unauthorized_handler
def unauthorized():
    # Log that the handler was triggered
    path = request.path if request and hasattr(request, 'path') else 'unknown'
    if os.environ.get('FLASK_ENV') == 'development':
        print(f"--- UNAUTHORIZED HANDLER TRIGGERED for {path} ---")
        print(f"Request method: {request.method}, Headers: {dict(request.headers)}")
        print(f"Cookies present: {bool(request.cookies)}")
    
    # Always return JSON
    return jsonify({
        'error': 'Unauthorized',
        'message': 'You must be logged in to access this resource',
        'path': path
    }), 401

# Custom Jinja2 filters
def basename_filter(path):
    return os.path.basename(path)

def nl2br_filter(text):
    if not text:
        return ""
    return text.replace('\n', '<br>')

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
        
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    
    # Ensure secret key is set
    if not app.config.get('SECRET_KEY'):
        if config_name == 'production':
            raise ValueError("SECRET_KEY must be set via environment variable in production!")
        else:
            app.logger.warning("Using default development SECRET_KEY. Set a proper SECRET_KEY environment variable.")
            app.config['SECRET_KEY'] = 'dev-key-please-change-in-production'

    # Initialize Sentry
    init_sentry(app)

    # Register custom Jinja2 filters
    app.jinja_env.filters['basename'] = basename_filter
    app.jinja_env.filters['nl2br'] = nl2br_filter
    
    # Use custom session interface
    app.session_interface = CustomSessionInterface()
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    
    # Initialize JWT
    from .jwt_config import init_jwt
    jwt = init_jwt(app)

    # Add security headers to all responses
    @app.after_request
    def add_security_headers(response):
        # Add basic security headers for development
        # These should be more restrictive in production
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Add Content-Security-Policy in development
        # This should be more restrictive in production
        if app.config['DEBUG']:
            csp = "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self' *.ingest.sentry.io"
        else:
            # More restrictive CSP for production
            csp = "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; connect-src 'self' *.ingest.sentry.io"
        
        # Only set Content-Security-Policy for HTML responses to avoid breaking API calls
        if response.mimetype == 'text/html':
            response.headers['Content-Security-Policy'] = csp
            
        return response
        
    # Database connection error handler
    @app.errorhandler(Exception)
    def handle_db_exceptions(e):
        import sqlalchemy.exc
        from pymysql import MySQLError
        
        # Handle specific database-related exceptions
        if isinstance(e, (sqlalchemy.exc.OperationalError, 
                         sqlalchemy.exc.InternalError,
                         sqlalchemy.exc.DisconnectionError, 
                         MySQLError)):
            # Log detailed error for debugging
            app.logger.error(f"Database error: {str(e)}")
            
            # For API routes, return JSON error
            if request.path.startswith('/api/'):
                return jsonify({
                    'error': 'Database error',
                    'message': 'A database connection error occurred. Please try again later.'
                }), 500
            
            # For regular routes, show user-friendly error page
            return render_template('errors/db_error.html'), 500
            
        # Let Flask handle other exceptions normally
        return e

    # Conditional CORS Setup
    if app.config['DEBUG']:
        # Development CORS (more permissive)
        allowed_origins = [
            "http://localhost:3001", 
            "http://localhost:3002", 
            "http://172.16.16.6:3001", 
            "http://172.16.16.6:5004",
            "http://172.16.16.6",
            "http://172.16.16.26", 
            "http://172.16.16.26:3001",
            "http://172.16.16.26:5004"
        ]
        
        # Create a basic CORS configuration first
        cors = CORS(app, 
                  resources={r"/*": {"origins": "*"}},  # Start with a permissive setting
                  supports_credentials=True)
        
        # Then manually handle CORS for specific routes with after_request
        @app.after_request
        def handle_cors(response):
            # Only modify headers for API requests to avoid conflicting with other middleware
            if request.path.startswith('/api/'):
                origin = request.headers.get('Origin')
                if origin in allowed_origins:
                    # Clear any existing CORS headers to avoid duplicates
                    for header in list(response.headers.keys()):
                        if header.startswith('Access-Control-'):
                            del response.headers[header]
                    
                    # Set the proper CORS headers for the specific origin
                    response.headers['Access-Control-Allow-Origin'] = origin
                    response.headers['Access-Control-Allow-Credentials'] = 'true'
                    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
                    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, X-CSRF-TOKEN, X-CSRFToken, x-csrf-token, Expires, Cache-Control, Pragma'
                    response.headers['Vary'] = 'Origin'
            
            return response
        
        app.logger.info(f"Development CORS enabled for: {', '.join(allowed_origins)}")
    else:
        # Production CORS (restrictive)
        allowed_origins = [app.config.get('BASE_URL')] # Use BASE_URL from config
        if not allowed_origins[0]:
             raise ValueError("BASE_URL must be configured for production CORS.")
        
        # Create a basic CORS configuration first
        cors = CORS(app, 
                  resources={r"/api/*": {"origins": allowed_origins[0]}},
                  supports_credentials=True)
        
        # Then manually handle CORS for specific routes with after_request
        @app.after_request
        def handle_cors(response):
            # Only modify headers for API requests
            if request.path.startswith('/api/'):
                origin = request.headers.get('Origin')
                if origin == allowed_origins[0]:
                    # Clear any existing CORS headers to avoid duplicates
                    for header in list(response.headers.keys()):
                        if header.startswith('Access-Control-'):
                            del response.headers[header]
                    
                    # Set the proper CORS headers for the specific origin
                    response.headers['Access-Control-Allow-Origin'] = origin
                    response.headers['Access-Control-Allow-Credentials'] = 'true'
                    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
                    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, X-CSRF-TOKEN, X-CSRFToken, x-csrf-token, Expires, Cache-Control, Pragma'
                    response.headers['Vary'] = 'Origin'
            
            return response
        
        app.logger.info(f"Production CORS enabled for: {allowed_origins[0]}")

    from .auth_routes import auth as auth_blueprint
    from .routes import bp as main_blueprint
    from .admin_routes import admin_bp as admin_blueprint
    from .violation_routes import violation_bp as violations_blueprint
    from .user_routes import user_api as users_blueprint
    from .dashboard_routes import dashboard as dashboard_blueprint
    from .unit_routes import unit_bp as unit_blueprint
    from .test_jwt_routes import test_jwt_bp as test_jwt_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(violations_blueprint)
    app.register_blueprint(users_blueprint)
    app.register_blueprint(dashboard_blueprint)
    app.register_blueprint(unit_blueprint)
    app.register_blueprint(test_jwt_blueprint)
    
    # Load SMTP settings from database when the app is fully initialized
    with app.app_context():
        try:
            from .models import Settings
            settings = Settings.get_settings()
            
            # Only apply if all required settings are present
            if (settings.smtp_server and settings.smtp_port and 
                settings.smtp_username and settings.smtp_password):
                
                # Apply settings to app configuration
                app.config['MAIL_SERVER'] = settings.smtp_server
                app.config['MAIL_PORT'] = settings.smtp_port
                app.config['MAIL_USERNAME'] = settings.smtp_username
                app.config['MAIL_PASSWORD'] = settings.smtp_password
                app.config['MAIL_USE_TLS'] = settings.smtp_use_tls
                
                # Set default sender if available
                if settings.smtp_from_email:
                    if settings.smtp_from_name:
                        sender = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
                    else:
                        sender = settings.smtp_from_email
                    app.config['MAIL_DEFAULT_SENDER'] = sender
                
                # Reinitialize mail with the new configuration
                mail.init_app(app)
                
                app.logger.info(f"SMTP settings loaded from database: {settings.smtp_server}:{settings.smtp_port}")
            else:
                missing = []
                if not settings.smtp_server:
                    missing.append("SMTP Server")
                if not settings.smtp_port:
                    missing.append("SMTP Port")
                if not settings.smtp_username:
                    missing.append("SMTP Username")
                if not settings.smtp_password:
                    missing.append("SMTP Password")
                
                app.logger.warning(f"Could not load SMTP settings from database - missing: {', '.join(missing)}")
                app.logger.warning("Using default mail settings. Test emails may fail.")
        except Exception as e:
            app.logger.error(f"Error loading SMTP settings from database: {str(e)}")

    return app
