# Gotchas

This document lists known edge cases, caveats, workarounds, and potential issues.

## Known Issues
- **F-string Backslash Escape Sequences**: Python f-strings cannot contain backslash escape sequences like `\n` in expression parts. These need to be handled separately using regular strings and `.format()` or by pre-formatting the content before including it in the f-string.
- **SQLite Date Handling**: SQLite expects Python date objects for date columns, not strings. Empty strings or incorrectly formatted date strings passed to date columns will cause a "SQLite Date type only accepts Python date objects as input" error. All date fields must be preprocessed to either valid date objects or None before being passed to the database.
- None documented yet.

## Edge Cases
- Login form: If the user submits an invalid email or password, the first error is displayed using flash messages or inline feedback.
- Login form (React): If the user submits an invalid email or password, the error is displayed inline below the form. The form requires both fields before submission.
- Login logo: If the logo fails to load from the path, a base64 fallback image is displayed automatically for reliability.
- CSRF: All forms must include CSRF tokens to prevent cross-site request forgery.
- Dynamic fields: If a field definition is changed (e.g., type or required status), existing violation records may have incompatible or missing values. UI and API should handle such cases gracefully.
- Deleting field definitions: Deleting a field definition should either cascade to field values or mark the field as inactive to preserve data integrity.
- Field order: Reordering fields must be reflected consistently in both admin and user forms.
- Validation: Ensure both backend and frontend enforce field validation rules to prevent inconsistent data.
- File upload: If a user attempts to upload a file with an unsupported or undetectable type, the upload will be rejected and an error message will be shown. Only specific document/image types are allowed (see implementation_details.md).
- File upload: If the server does not have python-magic installed, MIME type detection falls back to the browser-provided mimetype, which may be less reliable. This could result in some valid files being rejected or some invalid files being accepted (rare).
- File upload: If a file is rejected for type or virus, it is deleted immediately and not stored.
- Pagination: If a user requests a per_page or limit above 100, the API returns an error. If a value is missing or invalid, the API defaults to safe values (page=1, per_page=10).
- Pagination: All paginated endpoints strictly validate integer parameters and enforce maximums to prevent DoS. Error messages are returned for invalid or excessive values.

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

## Login Logo Troubleshooting

- If the login logo does not appear, ensure `logospectrum.png` exists in the public directory and is referenced with the correct path in the Login component.
- If the logo fails to load, a fallback will be shown, but check for typos or missing files if you want your custom branding.
- In the React login form, the base64 fallback ensures a logo is always shown even if the file is missing or the path is incorrect.

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

### WeasyPrint Version Compatibility Issues

The application uses WeasyPrint to generate PDF files from HTML. Version 61+ of WeasyPrint has a different API that can cause issues:

- **Error Message**: If you see `PDF.__init__() takes 1 positional argument but 3 were given` in the logs, this indicates a WeasyPrint API incompatibility
- **Root Cause**: Different versions of WeasyPrint expect different parameter formats when generating PDFs
- **Solution**: The application has been updated to use local imports and compatible parameter formats
- **Fallback Mechanism**: If direct HTML-to-PDF conversion fails, the system will:
  1. Try an alternative approach using temporary HTML files
  2. Create a valid but minimal PDF file with an error message if all generation methods fail
  3. Log detailed error information for troubleshooting

If PDF files don't open or show as corrupted in the browser:
1. Check application logs for "PDF generation error" messages
2. Verify that the generated PDF is valid using a command-line tool like `pdfinfo` or `file`
3. Try the alternative PDF generation method by editing a violation (this will regenerate the PDF)

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

## Violation Reply System

### Reply Form Considerations

- **Missing CSRF Protection**: The reply form does not currently include CSRF protection since it's designed to be accessible without authentication. Consider adding CSRF tokens if security concerns arise.
- **Email Verification**: The system does not verify that the email provided in the reply form belongs to the sender. Anyone could potentially submit a reply using any email address.
- **HTML in Responses**: The reply system sanitizes HTML input by default (through template escaping), but responses with formatting that resembles HTML might have their appearance affected.

### Reply Display Issues

- **Timestamp Display**: Reply timestamps are displayed in the server's local timezone. If the server and users are in different timezones, the displayed times may be confusing.
- **Long Responses**: Very long responses can affect the layout of the violation detail page. The system doesn't currently truncate or paginate responses.
- **Missing Replies**: If a violation has a large number of replies, it might affect the performance of the detail page loading and PDF generation.

### Email Notification Edge Cases

- **Reply To Original Creator**: If the creator's account has been deleted or their email address has changed, reply notifications might not reach them.
- **Notification Loops**: Be aware that if global notification emails are set up and people reply from those notification emails, it could create notification loops where everyone keeps getting notified about replies.
- **Email Formatting**: Multi-paragraph responses in emails might have their formatting altered slightly when rendered in email clients due to how HTML newlines are processed.

### PDF Generation with Replies

- **Large PDFs**: Violations with many replies will generate larger PDF files, which might affect download speeds and viewing performance.
- **File Size Limits**: Some email systems might reject attachments over certain sizes if PDFs with many replies are attached to emails.
- **Print Layout**: When printing PDFs with many replies, be aware that the layout might span multiple pages in ways that aren't optimal for reading.

### Database Considerations

- **Reply Storage Growth**: The `violation_replies` table will grow over time as more responses are added. Consider implementing archiving strategies for very old violations.
- **IP Address Privacy**: IP addresses stored with replies might be considered personal data under privacy regulations like GDPR. Ensure your data retention policies account for this.
- **Missing Relationships**: If a violation is deleted, all its replies should be deleted as well (cascading delete). This is implemented through the foreign key constraint but verify this behavior in testing.

## Static Violation Form Migration (2024)

- **Legacy Data:** Old violations with dynamic fields remain viewable. If a legacy field is not present in the static form, it will be displayed in a read-only/legacy section.
- **File Uploads:** File uploads are limited to specific types and sizes. If users encounter browser compatibility issues, recommend using Chrome or Firefox.
- **Dropdown Options:** If dropdown options need to change, a code update and redeployment is required. There is no longer a UI for admin-driven field changes.

# Static Violation Field Expansion (2024) - Gotchas & Edge Cases

- **Legacy Violations:** Violations created before June 2024 may not have values for the new static fields. API and UI must handle missing/null values gracefully.
- **File Uploads:** The `attach_evidence` field stores file metadata/paths as JSON or text. Ensure backward compatibility with any legacy file storage formats.
- **Migration:** The Alembic migration must be applied to all environments before deploying the updated code. If the migration is skipped, new violations will fail to save.
- **API Backward Compatibility:** API consumers expecting the old dynamic field structure must be updated to use the new static field names.
- **Validation:** Some fields are required in the frontend but nullable in the database for legacy compatibility. Always validate on both client and server.
- **Data Consistency:** Ensure that all new fields are included in API responses and are properly mapped in the model's `to_dict()` method.
- **Testing:** Test both creation and retrieval of violations with and without the new fields to ensure robust handling of all cases.

## Content Security Policy

- All generated HTML and PDFs include a restrictive CSP meta tag to prevent XSS. If you need to embed external images or fonts, you must adjust the policy in the template.

## Session Timeout, Idle Timeout, and Re-authentication

- Session Timeout: Users will be logged out after 24 hours or 30 minutes of inactivity. If users report unexpected logouts, check server time and browser cookie settings.
- Idle Timeout: If a user leaves a tab open and returns after 30+ minutes, they must log in again.
- Secure Cookies: SESSION_COOKIE_SECURE requires HTTPS in production. If users cannot stay logged in, check for mixed content or HTTP usage.
- Re-authentication: Sensitive actions require password re-entry within 5 minutes. If users are prompted too often, adjust the timeout in the decorator.

## Violation Detail Display

- If static fields (owner, tenant, details, etc.) or evidence are missing, check `ViolationDetail.js` rendering logic and the `/api/violations/public/...` API response.

## UUID URLs

- Ensure links from `ViolationList.js` use `/violations/public/:publicId`. If detail pages fail to load, check the API endpoint and the `public_id` value.

## Evidence Links

- If evidence links (`/evidence/...`) are broken, verify the base path in `ViolationDetail.js` and the file serving logic in `violation_routes.py` (`get_evidence_file`).

## New Edge Cases and Troubleshooting (June 2024)

- **CORS Misconfiguration**: If the frontend cannot access the backend API, verify that the backend's allowed origins include the correct IPs (e.g., 172.16.16.6, 172.16.16.26). CORS errors will appear in the browser console if not configured properly.
- **JWT Session Timeout/Password Recency**: If users are unexpectedly logged out or denied access, check the `enforce_session_timeouts` and `require_recent_password` logic. Ensure JWT tokens are refreshed and password recency is enforced as intended.
- **Telephone Validation**: The tenant "Telephone" field now requires a 10-digit number. Users may encounter validation errors if entering non-numeric or incorrectly formatted numbers. Format guidance is shown below the input.
- **UI Color Consistency**: Button colors in User Management and Unit Profiles have been standardized. If colors appear incorrect, verify CSS class assignments and ensure the latest styles are loaded.
- **Edit Button Placement**: The Edit button in Unit Profiles is now yellow and appears next to the View button. If missing, check for correct rendering logic and updated component code.
- **Unit Profile Display Issues**: If fields are missing or not visible in the unit profile page, ensure the latest frontend code is deployed and that the backend API returns all expected fields. Debug by checking API responses and React component props.
- **User Creation Fields (June 2024):** First Name, Last Name, and Position are now required for all new users. If any are missing or invalid, user creation will fail with a validation error.
- **Position Dropdown Validation:** Only the allowed values (Council, Property Manager, Caretaker, Cleaner, Concierge) are accepted. Any other value will be rejected by the backend.
- **Existing Users:** Existing users without first/last name or position will remain valid, but editing or re-saving may require these fields to be filled in.

---

*Update this file immediately when new issues, bugs, or edge cases are discovered.* 