#!/usr/bin/env python3
from app import create_app, db
from app.models import Settings
import getpass

app = create_app()

with app.app_context():
    settings = Settings.get_settings()
    
    # Print current settings
    print(f'Current SMTP Settings:')
    print(f'Server: {settings.smtp_server}')
    print(f'Port: {settings.smtp_port}')
    print(f'Username: {settings.smtp_username}')
    print(f'TLS Enabled: {settings.smtp_use_tls}')
    
    # Get new password
    print('\nEnter the new SMTP password:')
    new_password = getpass.getpass()
    
    # Update password
    settings.smtp_password = new_password
    db.session.commit()
    
    print('\nSMTP password updated successfully!') 