#!/usr/bin/env python3
from app import create_app, mail
from app.models import Settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
import getpass

# Create the app and get settings
app = create_app()
with app.app_context():
    settings = Settings.get_settings()
    
    # Print settings from the database
    print("=== SMTP Settings from Database ===")
    print(f"Server: {settings.smtp_server}")
    print(f"Port: {settings.smtp_port}")
    print(f"Username: {settings.smtp_username}")
    print(f"Password: {'[SET]' if settings.smtp_password else '[NOT SET]'}")
    print(f"TLS: {settings.smtp_use_tls}")
    print("")
    
    # Print Flask configuration
    print("=== Current Flask Mail Configuration ===")
    for key in ['MAIL_SERVER', 'MAIL_PORT', 'MAIL_USE_TLS', 'MAIL_USERNAME', 'MAIL_DEFAULT_SENDER']:
        print(f"{key}: {app.config.get(key)}")
    print("")
    
    # Display warning message about using admin UI
    print("NOTE: The recommended way to configure and test SMTP settings is through the admin UI settings page.")
    print("This script should only be used for troubleshooting purposes.")
    confirm = input("\nDo you want to proceed with testing the email configuration? (y/n): ")
    
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        sys.exit(0)
    
    # Ask for recipient email
    print("\nEnter the recipient email address:")
    to_email = input().strip()
    if not to_email or '@' not in to_email:
        print("Error: Invalid email address. Exiting.")
        sys.exit(1)
    
    # Apply settings directly to app config
    print("=== Applying SMTP Settings to Flask Config ===")
    app.config['MAIL_SERVER'] = settings.smtp_server
    app.config['MAIL_PORT'] = settings.smtp_port
    app.config['MAIL_USERNAME'] = settings.smtp_username
    app.config['MAIL_PASSWORD'] = settings.smtp_password
    app.config['MAIL_USE_TLS'] = settings.smtp_use_tls
    if settings.smtp_from_email:
        sender = settings.smtp_from_name + ' <' + settings.smtp_from_email + '>' if settings.smtp_from_name else settings.smtp_from_email
        app.config['MAIL_DEFAULT_SENDER'] = sender
    
    # Print updated Flask configuration
    print("=== Updated Flask Mail Configuration ===")
    for key in ['MAIL_SERVER', 'MAIL_PORT', 'MAIL_USE_TLS', 'MAIL_USERNAME', 'MAIL_DEFAULT_SENDER']:
        print(f"{key}: {app.config.get(key)}")
    print("")
    
    # Try sending a test email
    print("=== Sending Test Email ===")
    try:
        from flask_mail import Message
        msg = Message(
            subject="Test Email After Config Fix",
            recipients=[to_email],
            body="This is a test email sent after properly configuring Flask-Mail.",
            sender=app.config.get('MAIL_DEFAULT_SENDER')
        )
        mail.send(msg)
        print(f"✓ Success! Email sent to {to_email} using Flask-Mail after configuration fix.")
    except Exception as e:
        print(f"✗ Failed to send email after config fix: {str(e)}")
        
        # Try direct SMTP connection as a fallback
        print("\n=== Trying Direct SMTP Connection as Fallback ===")
        
        # Check if we need to get password
        if not settings.smtp_password:
            print("SMTP password not set in database. Please enter it:")
            smtp_password = getpass.getpass()
        else:
            smtp_password = settings.smtp_password
            
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = app.config.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')
            msg['To'] = to_email
            msg['Subject'] = "Test Email Using Direct SMTP"
            msg.attach(MIMEText("This is a test email sent using direct SMTP connection.", 'plain'))
            
            # Connect to server
            print(f"Connecting to {settings.smtp_server}:{settings.smtp_port}...")
            server = smtplib.SMTP(settings.smtp_server, settings.smtp_port, timeout=10)
            
            # Use TLS if enabled
            if settings.smtp_use_tls:
                print("Starting TLS...")
                server.starttls()
            
            # Login
            print(f"Logging in as {settings.smtp_username}...")
            server.login(settings.smtp_username, smtp_password)
            
            # Send email
            print(f"Sending email to {to_email}...")
            server.send_message(msg)
            
            # Quit server
            server.quit()
            print(f"✓ Success! Email sent to {to_email} using direct SMTP connection.")
        except Exception as e:
            print(f"✗ Failed to send email using direct SMTP: {str(e)}")
            print("\nTroubleshooting tips:")
            print("1. Verify your SMTP settings in the admin UI")
            print("2. Check if your email provider requires specific settings")
            print("3. Review the application logs for more details")
            print("4. Some email providers may be blocking connections from your server") 