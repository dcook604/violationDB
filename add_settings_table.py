#!/usr/bin/env python3
import os
import sys

# Ensure we're in the correct path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Create a Flask app context
from app import create_app, db
from app.models import Settings
from sqlalchemy import text

app = create_app()

def upgrade_db():
    """Add the Settings table to the database"""
    with app.app_context():
        try:
            print("Creating Settings table...")
            sql = text('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY,
                smtp_server VARCHAR(255),
                smtp_port INTEGER,
                smtp_username VARCHAR(255),
                smtp_password VARCHAR(255),
                smtp_use_tls BOOLEAN DEFAULT 1,
                smtp_from_email VARCHAR(255),
                smtp_from_name VARCHAR(255),
                notification_emails TEXT,
                enable_global_notifications BOOLEAN DEFAULT 0,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_by INTEGER,
                FOREIGN KEY (updated_by) REFERENCES users (id)
            )
            ''')
            db.session.execute(sql)
            db.session.commit()
            
            # Create default settings if none exist
            settings = Settings.query.first()
            if not settings:
                print("Creating default settings...")
                settings = Settings(
                    smtp_server=app.config.get('MAIL_SERVER', 'localhost'),
                    smtp_port=app.config.get('MAIL_PORT', 25),
                    smtp_username=app.config.get('MAIL_USERNAME', ''),
                    smtp_password=app.config.get('MAIL_PASSWORD', ''),
                    smtp_use_tls=app.config.get('MAIL_USE_TLS', True),
                    smtp_from_email=app.config.get('MAIL_DEFAULT_SENDER', 'noreply@example.com'),
                    smtp_from_name='Violation System',
                    notification_emails='',
                    enable_global_notifications=False
                )
                db.session.add(settings)
                db.session.commit()
                print("Default settings created with ID:", settings.id)
            else:
                print("Settings already exist. No default settings created.")
                
            print("Settings table creation complete.")
            return True
        except Exception as e:
            print(f"Error creating Settings table: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    upgrade_db() 