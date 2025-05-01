"""
Module for loading email settings from the database into Flask Mail
"""
from flask import current_app
from .models import Settings

def load_smtp_settings():
    """
    Load SMTP settings from the database and apply them to Flask Mail configuration
    
    This function should be called at application startup to initialize Flask-Mail
    with the database settings.
    """
    try:
        settings = Settings.get_settings()
        
        # Only apply if all required settings are present
        if (settings.smtp_server and settings.smtp_port and 
            settings.smtp_username and settings.smtp_password):
            
            # Apply settings to app configuration
            current_app.config['MAIL_SERVER'] = settings.smtp_server
            current_app.config['MAIL_PORT'] = settings.smtp_port
            current_app.config['MAIL_USERNAME'] = settings.smtp_username
            current_app.config['MAIL_PASSWORD'] = settings.smtp_password
            current_app.config['MAIL_USE_TLS'] = settings.smtp_use_tls
            
            # Set default sender if available
            if settings.smtp_from_email:
                if settings.smtp_from_name:
                    sender = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
                else:
                    sender = settings.smtp_from_email
                current_app.config['MAIL_DEFAULT_SENDER'] = sender
            
            current_app.logger.info(f"SMTP settings loaded from database: {settings.smtp_server}:{settings.smtp_port}")
            return True
        else:
            current_app.logger.warning("Could not load SMTP settings from database - incomplete configuration")
            current_app.logger.warning(f"Server: {settings.smtp_server}, Port: {settings.smtp_port}, " +
                                      f"Username: {settings.smtp_username}, " +
                                      f"Password: {'[SET]' if settings.smtp_password else '[NOT SET]'}")
            return False
    except Exception as e:
        current_app.logger.error(f"Error loading SMTP settings from database: {str(e)}")
        return False 