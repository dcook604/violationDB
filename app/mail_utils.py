from flask import current_app, render_template
from flask_mail import Message
from . import mail
from .models import Settings
import logging

logger = logging.getLogger(__name__)

def send_password_reset_email(user_email, reset_link):
    """Sends the password reset email to the user."""
    try:
        settings = Settings.get_settings()
        if not settings or not settings.smtp_server or not settings.smtp_port or not settings.smtp_from_email:
            logger.error("SMTP settings are not configured. Cannot send password reset email.")
            # In a real app, you might raise an error or return False
            # For now, we'll log the error.
            return False

        # Sender format: "App Name <email@example.com>" or just "email@example.com"
        sender_email = settings.smtp_from_email
        sender_name = settings.smtp_from_name or 'Spectrum 4 Violation System' # Default name
        sender = f"{sender_name} <{sender_email}>"

        # Ensure Flask-Mail is configured with DB settings (usually done in create_app)
        # If not, we might need to configure it here temporarily, but that's less ideal.
        if not current_app.config.get('MAIL_SERVER'):
             logger.warning("Flask-Mail may not be configured with DB settings. Attempting to send anyway.")
             # Optionally force config update here if create_app doesn't handle it reliably
             # current_app.config.update(...)
             # mail.init_app(current_app) # Reinitialize if needed

        subject = "Reset Your Password - Spectrum 4 Violation System"
        # Need to get current year for the template
        from datetime import datetime
        current_year = datetime.utcnow().year
        html_body = render_template('email/password_reset.html', 
                                      reset_link=reset_link, 
                                      current_year=current_year)

        msg = Message(subject,
                      sender=sender,
                      recipients=[user_email],
                      html=html_body)

        mail.send(msg)
        logger.info(f"Password reset email successfully sent to {user_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send password reset email to {user_email}: {str(e)}", exc_info=True)
        return False 