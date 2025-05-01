import os
import logging
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_cors import CORS
from .config import Config
from datetime import timedelta
from flask.sessions import SecureCookieSessionInterface

# Custom session interface to fix SameSite issue
class CustomSessionInterface(SecureCookieSessionInterface):
    def get_cookie_samesite(self, app):
        # Use SameSite=Lax for development (works with HTTP)
        return 'Lax'

# Configure logging to save errors to flask_error.log
logging.basicConfig(
    filename='flask_error.log',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

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
    
    # Use custom session interface
    app.session_interface = CustomSessionInterface()
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Enable CORS for development with specific origins (not wildcards)
    CORS(app, 
         resources={r"/*": {
             "origins": ["http://localhost:3001", "http://localhost:3002"],
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
        if origin and origin in ['http://localhost:3001', 'http://localhost:3002']:
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

    return app
