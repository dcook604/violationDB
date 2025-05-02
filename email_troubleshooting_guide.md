# SMTP Email Troubleshooting Guide

## Issue Summary
The application is showing a "Connection refused" error when trying to send test emails, despite the SMTP settings being configured in the database.

Error message:
```
Failed to send test email: Failed to send test email: [Errno 111] Connection refused
```

## Root Causes Identified

1. **SMTP Configuration Issues**: The SMTP settings in the admin UI may be incorrect or incomplete.

2. **Network Connectivity**: The server may have connectivity issues with the SMTP server.

3. **Authentication Problems**: The saved credentials may be incorrect or the authentication might be failing.

4. **Code Issues**: The email sending function may not be properly applying the database settings.

## Proper Configuration Method

The correct way to configure SMTP settings is through the application's admin UI:

1. Log in as an administrator
2. Navigate to the Settings page
3. Enter your SMTP server details (server, port, username, password, etc.)
4. Use the "Test Email" feature to verify your configuration

## Step-by-Step Troubleshooting

### 1. Verify Settings in Admin UI

First, check the SMTP settings in the admin UI:
- SMTP Server: Should be correctly set (e.g., mail.smtp2go.com)
- SMTP Port: Use the appropriate port (e.g., 2525 or 587)
- SMTP Username: Verify correct username
- SMTP Password: Make sure password is set (you may need to re-enter it)
- TLS/SSL: Toggle based on your email provider's requirements

### 2. Test Connection and Authentication

If the settings appear correct but emails still fail, use our diagnostic tools:

```bash
# Test network connectivity
source venv/bin/activate
python check_network.py

# Test email using database settings
source venv/bin/activate
python test_email_directly.py
```

These scripts will:
- Use the SMTP settings from your database
- Test TCP connectivity to the server
- Attempt to authenticate with your credentials
- Provide detailed error messages

### 3. Check Logs for Specific Errors

When troubleshooting, always check the server logs:

```bash
tail -f flask_error.log
```

Look for specific error messages related to SMTP connections, like:
- Connection refused (network issue)
- Authentication failure (credential issue)
- Timeout (network latency issue)

### 4. Reset Password if Necessary

If you suspect a password issue but want to keep the UI configuration:

```bash
source venv/bin/activate
python fix_smtp_password.py
```

This script will:
- Show your current SMTP settings from the database
- Allow you to update only the password while preserving other settings
- Confirm the password was successfully stored

### 5. Restart the Application

After making any changes, restart your Flask application:

```bash
# Stop the current Flask server (if running)
pkill -f "flask run"

# Start it again
source venv/bin/activate
flask run --host=0.0.0.0 --port=5004
```

## Common SMTP Issues and Solutions

### Connection Refused

**Causes:**
- Incorrect SMTP server name
- Incorrect port number
- Firewall blocking outgoing connections
- SMTP server down or not accepting connections

**Solutions:**
- Verify server name and port in the admin UI
- Check if outgoing connections are allowed (firewall settings)
- Try an alternative port (587 or 465)

### Authentication Failures

**Causes:**
- Incorrect username or password
- Account requiring specific security settings
- Special characters in password causing encoding issues

**Solutions:**
- Update credentials in the admin UI
- Verify credentials directly with your email provider
- Use an app-specific password if 2FA is enabled

### TLS/SSL Issues

**Causes:**
- Incorrect TLS setting
- Server requiring TLS but setting disabled
- Missing certificates

**Solutions:**
- Toggle the TLS setting in the admin UI based on your provider's requirements
- For some providers like Gmail, TLS is required
- For others, you may need to try with and without TLS

## Going Forward

Remember that the admin UI is the proper way to configure email settings. The diagnostic scripts should only be used for troubleshooting, not as the primary configuration method.

If issues persist after trying all solutions:

1. Contact your SMTP provider to verify account status
2. Check for any IP restrictions on your SMTP service
3. Consider temporarily using an alternative SMTP service to isolate the issue

## References

* Flask-Mail documentation: https://pythonhosted.org/Flask-Mail/
* SMTP2GO documentation: https://www.smtp2go.com/docs/ 