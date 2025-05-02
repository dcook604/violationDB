import os
import logging
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_cors import CORS
from flask_migrate import Migrate
from .config import Config
from datetime import timedelta
from flask.sessions import SecureCookieSessionInterface
import os.path

# Custom session interface to fix SameSite issue
class CustomSessionInterface(SecureCookieSessionInterface):
    def get_cookie_samesite(self, app):
        # Use SameSite=Lax for development (works with HTTP)
        return 'Lax'

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

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))

# Add custom unauthorized handler for API requests
@login_manager.unauthorized_handler
def unauthorized():
    # Log that the handler was triggered
    path = request.path if request and hasattr(request, 'path') else 'unknown'
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

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Ensure secret key is set
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = 'dev-key-please-change-in-production'

    # Configure session and cookie settings for development
    app.config.update(
        SESSION_COOKIE_SAMESITE='Lax',  # Changed from None to Lax
        SESSION_COOKIE_SECURE=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_DOMAIN=None,
        PERMANENT_SESSION_LIFETIME=timedelta(days=31),
        REMEMBER_COOKIE_SAMESITE='Lax',  # Changed from None to Lax
        REMEMBER_COOKIE_SECURE=False,
        REMEMBER_COOKIE_HTTPONLY=True,
        REMEMBER_COOKIE_DURATION=timedelta(days=31)
    )
    
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

    # Enable CORS for development with specific origins (not wildcards)
    CORS(app, 
         resources={r"/*": {
             "origins": ["http://localhost:3001", "http://localhost:3002", "http://172.16.16.6:3001", "http://172.16.16.6:5004"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept"],
             "supports_credentials": True,
             "expose_headers": ["Content-Type", "Authorization"]
         }},
         supports_credentials=True)

    # Force CORS for every response
    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get('Origin')
        if origin and origin in ['http://localhost:3001', 'http://localhost:3002', 'http://172.16.16.6:3001', 'http://172.16.16.6:5004']:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept, Authorization, X-Requested-With'
            if request.method == 'OPTIONS':
                response.headers['Access-Control-Max-Age'] = '1728000'
        
        # Log response
        print(f"CORS Response for {request.path}: origin={origin}, status={response.status_code}, headers={dict(response.headers)}")
        return response

    from .auth_routes import auth as auth_blueprint
    from .routes import bp as main_blueprint
    from .admin_routes import admin_bp as admin_blueprint
    from .violation_routes import violation_bp as violations_blueprint
    from .user_routes import user_api as users_blueprint
    from .dashboard_routes import dashboard as dashboard_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(violations_blueprint)
    app.register_blueprint(users_blueprint)
    app.register_blueprint(dashboard_blueprint)
    
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
