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
    
    # Default Database (SQLite for development)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
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
    
    # Default Session and Cookie Settings (less secure for development)
    SESSION_COOKIE_SECURE = False 
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'  
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
    # Development specific settings can go here if needed
    BASE_URL = os.environ.get('BASE_URL') or 'http://localhost:5004' # Or your dev IP

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True # Ensure HTTPS is used
    REMEMBER_COOKIE_SECURE = True # Ensure HTTPS is used
    
    # Production Database (MySQL) - Read from environment or use provided details
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