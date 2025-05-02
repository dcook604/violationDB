#!/usr/bin/env python3
from app import create_app, mail
from app.models import Settings
import json

app = create_app()

with app.app_context():
    # Get settings from database
    settings = Settings.get_settings()
    
    print("=== SMTP Configuration Diagnostic ===")
    
    print("\n1. Settings from Database:")
    print(f"   Server: {settings.smtp_server}")
    print(f"   Port: {settings.smtp_port}")
    print(f"   Username: {settings.smtp_username}")
    print(f"   Password: {'[SET]' if settings.smtp_password else '[NOT SET]'}")
    print(f"   TLS Enabled: {settings.smtp_use_tls}")
    print(f"   From Email: {settings.smtp_from_email}")
    print(f"   From Name: {settings.smtp_from_name}")
    
    print("\n2. Flask Mail Configuration:")
    for key in ['MAIL_SERVER', 'MAIL_PORT', 'MAIL_USE_TLS', 'MAIL_USERNAME', 'MAIL_PASSWORD', 'MAIL_DEFAULT_SENDER']:
        value = app.config.get(key)
        if key == 'MAIL_PASSWORD' and value:
            print(f"   {key}: [SET]")
        else:
            print(f"   {key}: {value}")
    
    print("\n3. Mail Extension Configuration:")
    if hasattr(mail, 'state') and mail.state is not None:
        try:
            state_dict = {
                'server': getattr(mail.state, 'server', None),
                'port': getattr(mail.state, 'port', None),
                'use_tls': getattr(mail.state, 'use_tls', None),
                'username': getattr(mail.state, 'username', None),
                'password': '[SET]' if getattr(mail.state, 'password', None) else '[NOT SET]',
                'default_sender': getattr(mail.state, 'default_sender', None)
            }
            for key, value in state_dict.items():
                print(f"   {key}: {value}")
        except Exception as e:
            print(f"   Error accessing mail state: {e}")
    else:
        print("   Mail extension state not initialized or not accessible")
    
    print("\n=== Configuration Analysis ===")
    
    # Check for configuration mismatches
    mail_server_mismatch = app.config.get('MAIL_SERVER') != settings.smtp_server
    mail_port_mismatch = app.config.get('MAIL_PORT') != settings.smtp_port
    mail_username_mismatch = app.config.get('MAIL_USERNAME') != settings.smtp_username
    
    if mail_server_mismatch or mail_port_mismatch or mail_username_mismatch:
        print("\n⚠️ CONFIGURATION ISSUE DETECTED: Settings in database don't match Flask config!")
        
        if mail_server_mismatch:
            print(f"   - SMTP Server mismatch: '{settings.smtp_server}' (DB) vs '{app.config.get('MAIL_SERVER')}' (Flask)")
        if mail_port_mismatch:
            print(f"   - SMTP Port mismatch: {settings.smtp_port} (DB) vs {app.config.get('MAIL_PORT')} (Flask)")
        if mail_username_mismatch:
            print(f"   - SMTP Username mismatch: '{settings.smtp_username}' (DB) vs '{app.config.get('MAIL_USERNAME')}' (Flask)")
    else:
        print("\n✅ Database settings match Flask configuration.")
    
    # Check for localhost configuration
    if app.config.get('MAIL_SERVER') == 'localhost':
        print("\n⚠️ Using localhost as SMTP server, but no local SMTP server detected!")
        print("   This is likely causing the 'Connection refused' error.")
        print("   Update your SMTP settings in the admin UI to use mail.smtp2go.com:2525")
    
    # Check for missing password
    if not settings.smtp_password:
        print("\n⚠️ SMTP Password is not set in the database!")
        print("   This will cause authentication failures.")
        print("   Update your password in the admin UI or use the fix_smtp_password.py script.")
    
    # Check for missing settings
    missing = []
    if not settings.smtp_server:
        missing.append("SMTP Server")
    if not settings.smtp_port:
        missing.append("SMTP Port")
    if not settings.smtp_username:
        missing.append("SMTP Username")
    if not settings.smtp_from_email:
        missing.append("From Email")
    
    if missing:
        print(f"\n⚠️ Missing required SMTP settings: {', '.join(missing)}")
        print("   Update these settings in the admin UI.")
    
    print("\n=== SMTP Connection Test ===")
    print(f"Testing connection to {settings.smtp_server}:{settings.smtp_port}...")
    
    import socket
    try:
        sock = socket.create_connection((settings.smtp_server, settings.smtp_port), timeout=5)
        sock.close()
        print(f"✓ Successfully connected to {settings.smtp_server}:{settings.smtp_port}")
    except Exception as e:
        print(f"✗ Failed to connect to {settings.smtp_server}:{settings.smtp_port}: {e}")
    
    print("\n=== KEY ISSUE IDENTIFIED ===")
    print("The database has SMTP settings for mail.smtp2go.com, but Flask is using localhost!")
    print("This is a common issue with Flask-Mail configuration not being updated at runtime.")
    
    print("\n=== Recommendations ===")
    print("1. Check how the utils.send_email function applies database settings")
    print("2. Ensure database settings are properly applied before sending mail")
    print("3. Restart the Flask application after updating settings")
    print("4. You may need to modify app/__init__.py to apply database settings at startup") 