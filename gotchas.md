# Gotchas & Edge Cases

This file documents known issues, edge cases, and warnings for the Strata Violation Log application.

## Known Issues
- None documented yet.

## Edge Cases
- Login form: If the user submits an invalid email or password, the first error is displayed using flash messages or inline feedback.
- CSRF: All forms must include CSRF tokens to prevent cross-site request forgery.
- Dynamic fields: If a field definition is changed (e.g., type or required status), existing violation records may have incompatible or missing values. UI and API should handle such cases gracefully.
- Deleting field definitions: Deleting a field definition should either cascade to field values or mark the field as inactive to preserve data integrity.
- Field order: Reordering fields must be reflected consistently in both admin and user forms.
- Validation: Ensure both backend and frontend enforce field validation rules to prevent inconsistent data.

## Warnings
- Ensure that all static assets are correctly referenced using `url_for('static', ...)` to avoid broken links.

## Additional Notes
- If running React and Flask on different ports during development, ensure CORS is enabled on Flask (`flask-cors` or manual headers).
- For session/cookie authentication, set `withCredentials: true` in Axios and ensure Flask sends cookies with CORS responses.
- If field definitions are changed while a user is filling a form, validation errors may occur; handle gracefully in the UI.
- Drag-and-drop reordering requires unique field IDs and correct API ordering.
- The /api/violations endpoint is required for the React SPA ViolationList page. If not present, the list will not load.
- If user roles are not set up correctly, regular users may see no violations or too many. Ensure current_user.is_admin is reliable.
- Dynamic fields are returned as a nested object; if field definitions change, frontend may need to handle missing/extra columns.
- The /api/violations/:id endpoint is role-protected. Only admins or the creator can edit or delete a violation.
- When editing, ensure dynamic field names match backend definitions; missing fields may be lost if not included in the update.

## Database Schema Inconsistencies

### Issue: Model-Database Column Mismatch
The SQLAlchemy models define columns that don't exist in the actual database schema. This causes 500 errors when the application tries to query these non-existent columns.

Specific issues:
- The `Violation` model includes fields like `resolved_at` and `resolved_by` that don't exist in the database
- This affects routes that query these columns, particularly the dashboard statistics and violation listing endpoints

### Solution Approaches

1. **ORM-Safe Attribute Access**
   - Use `getattr(model, 'attribute', default_value)` instead of direct attribute access
   - Add `hasattr()` checks before accessing attributes that might not exist
   - Wrap operations in try-except blocks to gracefully handle missing column errors

2. **Raw SQL Queries**
   - For critical routes, use raw SQL queries with `db.session.execute(text(sql))` that only reference columns known to exist
   - This bypasses ORM mapping issues when there's a mismatch between models and schema

3. **Graceful Error Handling**
   - Return sensible defaults instead of 500 errors when database inconsistencies occur
   - Log detailed error information for debugging while providing a functional UI

### Lessons Learned
- Always ensure database migrations are in sync with model changes
- Test on a development database before deploying model changes
- Include robust error handling for database operations, especially in API endpoints
- Consider versioning APIs to handle schema evolution more gracefully

### Long-term Solutions
- Run database migrations to add missing columns
- Use Alembic to properly track schema changes
- Implement proper database versioning
- Consider soft schema validation on application startup

## Authentication and API Troubleshooting

### Common Authentication Issues
- **Gateway Timeout (504) Errors**: If the frontend proxy is misconfigured, it may attempt to proxy to incorrect endpoints or use the wrong port. Use the direct API connection method in `api.js` (set `baseURL`) to bypass proxy issues.
- **CORS Errors**: Ensure the backend CORS configuration allows the frontend origin and that `credentials: include` or `withCredentials: true` is set for all API requests.
- **Cookie Not Set/Sent**: Authentication depends on cookies being properly set and sent. Ensure:
  - `SameSite=Lax` is configured on backend cookies
  - Frontend and backend domains align (both on localhost or same domain)
  - `withCredentials` is set for AJAX requests
  - Session cookie configuration matches browser security requirements

### API Endpoint Troubleshooting
- Always test endpoints directly (e.g., with curl or browser) before integrating with frontend
- HTTP status 405 (Method Not Allowed) when accessing POST endpoints via GET indicates the endpoint exists but requires the correct method
- For authentication issues, check both Flask logs and browser network tab for full request/response details

### Server Management
- Never run multiple instances of the Flask server on the same port
- Use the provided `reset_servers.sh` script to ensure clean server restarts
- Always check logs (`flask.log` and `frontend/react.log`) when troubleshooting issues

## PDF Generation

### WeasyPrint Dependencies

WeasyPrint requires several system dependencies that might not be installed by default:

- In Ubuntu/Debian: `apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info`
- In CentOS/RHEL: `yum install gcc python3-devel python3-pip python3-setuptools python3-wheel python3-cffi cairo pango gdk-pixbuf2`
- In Alpine: `apk add build-base python3-dev py3-pip py3-setuptools py3-wheel py3-cffi cairo pango gdk-pixbuf`

### PDF Generation Failures

The system has fallback mechanisms for PDF generation failures:

1. If the first attempt to generate a PDF fails, a second approach is tried.
2. If both attempts fail, a placeholder file is created to ensure the path exists.
3. Errors are logged to `flask_error.log` for debugging.

### Common Issues

- **Missing Dependencies**: If WeasyPrint fails with system errors, ensure all required dependencies are installed.
- **Large or Complex Documents**: PDF generation may fail for very large or complex documents with many images.
- **CSS Compatibility**: Not all CSS features are supported by WeasyPrint. Stick to basic styling for best results.
- **Font Issues**: Custom fonts may not render correctly. Use web-safe fonts when possible.

### Environment-Specific Issues

- **Docker Containers**: May require additional configuration to install all WeasyPrint dependencies.
- **Production Servers**: Need to ensure the process has write permissions to the PDF output directory.
- **Memory Constraints**: Large PDFs may require more memory. Consider setting resource limits accordingly.

## Email Settings and Configuration Issues

### SMTP Server Authentication

- **Plain text password storage**: The SMTP password is stored as plain text in the database. Ensure database access is properly secured.
- **Gmail and other services**: Gmail and other modern email services often require "App Passwords" or reduced security settings for SMTP access.
- **TLS/SSL Issues**: Some email services strictly require TLS. If emails fail to send, ensure the TLS checkbox is enabled.
- **Port Numbers**: Common SMTP ports are 25 (non-secure), 465 (SSL), and 587 (TLS). Using the wrong port will cause connection failures.

### SMTP Connection Troubleshooting

- **Connection refused errors**: If you see "Connection refused" errors (Errno 111), check that:
  - The SMTP server address is correct and reachable from your network
  - The port is not blocked by a firewall
  - The server is actually running an SMTP service on that port
- **Authentication failures**: If connection succeeds but authentication fails, verify:
  - Username and password are correct
  - The account has permission to send via SMTP
  - Any security settings on the email provider are properly configured
- **Network connectivity**: Use the diagnostic scripts (check_network.py, test_smtp_connection.py) to verify basic connectivity before attempting to send emails
- **Socket timeouts**: Increase timeout values if your network has high latency or the SMTP server is slow to respond

### Dynamic Configuration Behavior

- **Per-email configuration**: The application loads SMTP settings from the database for each email operation
- **Testing after changes**: Always send a test email after changing SMTP settings
- **Logging location**: Check flask_error.log for detailed error messages if email sending fails
- **Socket testing**: The application attempts a direct socket connection test before trying SMTP to provide clearer error messages

### Global Notification Emails

- **Format sensitivity**: Email addresses must be properly comma-separated without extra spaces or characters.
- **Rate limiting**: Sending to many recipients can trigger rate limits on some SMTP servers. If using global notifications for many recipients, consider using a high-volume email service.
- **Email privacy**: Using BCC for large recipient lists is recommended for privacy but not currently implemented. Recipients will see all other email addresses in the To: field.
- **Duplicate removal**: The system removes duplicate email addresses to prevent multiple emails to the same recipient. This works on exact matches only, so variations in capitalization or formatting may result in duplicate emails.

### Configuration Changes

- **No immediate effect on existing processes**: Changes to email settings only affect new email sending operations, not any that are currently in progress.
- **No restart required**: SMTP settings are loaded dynamically for each email operation, so no application restart is needed.
- **Testing recommended**: Always use the "Send Test Email" feature to verify new settings before relying on them for actual notifications.

### SMTP Settings UI Issues

- **TLS/SSL Checkbox**: If the TLS/SSL checkbox doesn't seem to save its state correctly, ensure you're clicking directly on the checkbox (not just the label) and verify in the logs that the setting is being updated. This has been fixed in the latest version.
  - The issue was that the API's GET endpoint used `or True` as a default value, causing database 'false' values to be overridden.
  - This made it appear as if the checkbox was always returning to "enabled" even when the database stored "disabled".
- **Empty Password**: When updating other SMTP settings, leaving the password field empty will preserve the existing password, rather than clearing it.
- **Port Numbers**: Changing the port may trigger an automatic TLS mode based on common conventions (ports 465 and 587 typically use TLS, while 25 often doesn't).

---

*Update this file immediately when new issues, bugs, or edge cases are discovered.* 