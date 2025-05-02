#!/usr/bin/env python3
from app import create_app, db
from app.models import Settings
import getpass
import sys

app = create_app()

# No hardcoded values - we'll use interactive mode only
with app.app_context():
    settings = Settings.get_settings()
    
    # Print current settings
    print("=== Current SMTP Settings ===")
    print(f"Server: {settings.smtp_server}")
    print(f"Port: {settings.smtp_port}")
    print(f"Username: {settings.smtp_username}")
    print(f"Password: {'[SET]' if settings.smtp_password else '[NOT SET]'}")
    print(f"TLS Enabled: {settings.smtp_use_tls}")
    
    # Ask for confirmation before proceeding
    print("\nNOTE: The recommended way to update SMTP settings is through the admin UI settings page.")
    print("This script should only be used for troubleshooting purposes.")
    confirm = input("\nDo you want to proceed with updating just the password? (y/n): ")
    
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        sys.exit(0)
    
    # Get new password
    print("\nEnter your SMTP password for the configured server:")
    new_password = getpass.getpass()
    
    if not new_password:
        print("Error: Password cannot be empty. Exiting.")
        sys.exit(1)
    
    # Update password
    settings.smtp_password = new_password
    db.session.commit()
    
    # Verify the password was stored
    settings = Settings.query.first()  # Re-fetch to verify
    print("\n=== Updated SMTP Settings ===")
    print(f"Server: {settings.smtp_server}")
    print(f"Port: {settings.smtp_port}")
    print(f"Username: {settings.smtp_username}")
    print(f"Password: {'[SET]' if settings.smtp_password else '[NOT SET]'}")
    print(f"Password Length: {len(settings.smtp_password or '')}")
    print(f"TLS Enabled: {settings.smtp_use_tls}")
    
    print("\nPassword has been successfully updated.")
    print("Next step: Restart your Flask application for the changes to take effect.") 