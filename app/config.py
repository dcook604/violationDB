import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'mariadb://violationuser:viopass@127.0.0.1:3306/violationdb')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER', '172.19.0.6')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 25))
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@strata.local')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(os.path.dirname(__file__), 'uploads'))
    
    # Session and Cookie Settings
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = None  # Required for cross-domain cookies in development
    REMEMBER_COOKIE_SAMESITE = None  # Required for cross-domain cookies in development
    SESSION_COOKIE_DOMAIN = None  # Allow cookies to work across subdomains
    REMEMBER_COOKIE_DOMAIN = None  # Allow remember cookies to work across subdomains
    SESSION_PROTECTION = 'strong'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours in seconds