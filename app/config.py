import os
from dotenv import load_dotenv
from datetime import timedelta
import warnings

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(os.path.dirname(basedir), '.env'))

class Config:
    # Base configuration - Values here might be overridden by environment variables or specific configs
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'development-key-change-me' # MUST be set via env var in production
    BASE_DIR = os.path.dirname(basedir)
    
    # Sentry configuration
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    
    # Default Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://violation:n2hm13i@localhost:3309/violationdb'
    
    # Connection pooling settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,          # Default number of database connections in the pool
        'max_overflow': 20,       # Maximum number of connections to create above pool_size
        'pool_timeout': 30,       # Seconds to wait before giving up on getting a connection
        'pool_recycle': 1800,     # Recycle connections after 30 minutes to avoid stale connections
        'pool_pre_ping': True,    # Issue a test query on the connection to check if it's still valid
    }
    
    # General SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Default Email settings (use environment variables for production)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'localhost'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@example.com'
    
    # Upload folder
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit for uploads
    
    # Default SSL redirect (False for development)
    SSL_REDIRECT = False
    
    # Default Session and Cookie Settings (secure for production)
    SESSION_COOKIE_SECURE = True  # Only sent over HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Not accessible via JavaScript
    SESSION_COOKIE_SAMESITE = 'Lax'  # Prevent CSRF
    REMEMBER_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_DOMAIN = None
    REMEMBER_COOKIE_DOMAIN = None
    SESSION_PROTECTION = 'strong'
    
    # Session timeout settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24) # Absolute timeout
    IDLE_TIMEOUT_MINUTES = 30 # Idle timeout
    
    # Custom application settings
    ENFORCE_SINGLE_SESSION = True
    DEBUG = False # Default to False

class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False  # Override for HTTP development
    REMEMBER_COOKIE_SECURE = False # Also override this if used
    # Development specific settings can go here if needed
    BASE_URL = os.environ.get('BASE_URL') or 'http://localhost:5004' # Or your dev IP

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True # Ensure HTTPS is used
    REMEMBER_COOKIE_SECURE = True # Ensure HTTPS is used
    
    # Production Database (MySQL/MariaDB) configuration
    # --- WARNING: Hardcoding credentials here is NOT recommended for production! ---
    # --- It's better to set DATABASE_URL as an environment variable on your server. ---
    MYSQL_ROOT_PASSWORD = "n2hm13i" # Hardcoded as requested, but strongly discouraged
    MYSQL_DATABASE = "violationdb"
    MYSQL_USER = "violation"
    MYSQL_PASSWORD = "n2hm13i" # Hardcoded as requested, but strongly discouraged
    MYSQL_HOST = "localhost"
    MYSQL_PORT = "3309"
    
    # Construct the URI, issue warning if using hardcoded values from above
    prod_db_url = os.environ.get('DATABASE_URL')
    if not prod_db_url:
        warnings.warn(
            "DATABASE_URL environment variable not set. Falling back to hardcoded MySQL credentials "
            "in ProductionConfig. This is NOT recommended for production environments. "
            "Set the DATABASE_URL environment variable (e.g., mysql+mysqlclient://user:pass@host:port/db)", 
            UserWarning
        )
        prod_db_url = f"mysql+mysqlclient://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
        
    SQLALCHEMY_DATABASE_URI = prod_db_url
    
    # Production-specific connection pooling - more conservative for production
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 5,           # Start with fewer connections for better server resource management
        'max_overflow': 10,       # Allow fewer overflow connections
        'pool_timeout': 60,       # Wait longer in production before giving up
        'pool_recycle': 1800,     # Recycle connections after 30 minutes (match MariaDB wait_timeout)
        'pool_pre_ping': True,    # Always verify connection is valid before using it
    }

    # Base URL for production
    BASE_URL = os.environ.get('BASE_URL') or 'https://violation.spectrum4.ca'

    # Production Email - Ensure MAIL_* env vars are set on the server
    # Add any specific production email overrides if needed

    # SSL Redirect - Assuming handled by reverse proxy (Nginx/Cloudflare)
    SSL_REDIRECT = False 

# Dictionary to map config names to classes
config_by_name = dict(
    development=DevelopmentConfig,
    production=ProductionConfig,
    default=DevelopmentConfig
)