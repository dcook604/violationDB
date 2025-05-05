# User Management System - Gotchas and Edge Cases

## Password Management

### Temporary Password Issues
1. **Expiration Timing**
   - Temporary passwords expire after 24 hours
   - Server timezone affects expiration calculation
   - Use UTC consistently for all datetime operations

2. **Password Reset Conflicts**
   - Multiple temporary passwords may cause confusion
   - Always clear existing temporary password before setting new one
   - Ensure proper error handling during password updates

3. **Session Management**
   - User sessions should be invalidated after password changes
   - Temporary password login should force immediate password change
   - Handle concurrent login attempts appropriately

## Role Management

### Role Change Effects
1. **Admin Role**
   - Setting role to 'admin' automatically sets `is_admin=True`
   - Changing from 'admin' role doesn't automatically remove admin status
   - Use `set_role()` method to ensure proper role transitions

2. **Active Status**
   - Admin users are always active
   - Deactivating an admin requires role change first
   - Role changes don't affect active status unless becoming admin

## Database Operations

### Common Issues
1. **Unique Email Constraint**
   - Email uniqueness is enforced at database level
   - Handle IntegrityError for duplicate email addresses
   - Provide clear user feedback for email conflicts

2. **Session Management**
   - Always use try/except blocks with session operations
   - Implement proper session rollback on errors
   - Commit changes only after all operations succeed

## Security Considerations

### Password Security
1. **Password Hashing**
   - Never store plain-text passwords
   - Use werkzeug's password hashing functions
   - Handle hash generation errors gracefully

2. **Temporary Password Display**
   - Only show temporary password once during creation
   - Log temporary password generation attempts
   - Consider implementing secure password delivery mechanism

### Access Control
1. **Route Protection**
   - Always apply @login_required decorator
   - Check user permissions in route handlers
   - Handle unauthorized access attempts gracefully

2. **Form Validation**
   - Validate all form inputs server-side
   - Handle malformed data gracefully
   - Prevent role escalation attacks 

## PDF Generation Issues

### WeasyPrint Compatibility
1. **WeasyPrint 61.2 and pydyf Issues**
   - WeasyPrint 61.2 has known compatibility issues with the pydyf library
   - Direct rendering to memory buffer may fail with certain versions
   - If upgrading WeasyPrint, ensure thorough testing of PDF generation

2. **Fallback Mechanisms**
   - The system implements multiple fallback methods for PDF generation
   - Fallbacks occur in this order: direct rendering → temporary file approach → wkhtmltopdf
   - Each fallback attempt is logged for debugging purposes

3. **Error Handling**
   - All PDF generation attempts are wrapped in try/except blocks
   - Failed attempts are logged with detailed error messages
   - Final fallback failure raises PDFGenerationError

### Dynamic Fields in PDFs
1. **File Type Fields**
   - File type fields require special handling in PDF generation
   - URLs for uploaded files must be absolute in PDF context
   - Test PDF generation with various file upload scenarios

2. **Large Content**
   - Very large or complex violations may cause PDF generation to slow down
   - Extremely large violations may exceed memory limits during PDF generation
   - Consider implementing timeout handling for PDF generation 

## Loading State Management

### Global Window Properties
1. **Window Property Persistence**
   - `window.isUploadingFiles` and `window.latestViolationId` are global variables
   - These values persist between page navigations within the same browser session
   - Always reset these values after use or they may affect subsequent violation submissions

2. **Navigation During Loading**
   - Navigating away during file uploads may interrupt the process
   - Loading overlay blocks interaction but doesn't prevent manual navigation
   - Consider implementing a warning message for navigation attempts during uploads

### Loading Overlay Styling
1. **Opacity Issues**
   - `bg-opacity-${opacity}` requires Tailwind class purging considerations
   - Values outside the default Tailwind opacity scale may not be included in production builds
   - Stick to standard Tailwind opacity values (0, 25, 50, 75, 100) or use inline styles

2. **Z-Index Conflicts**
   - LoadingOverlay uses `z-50` which may conflict with other high z-index elements
   - Modal dialogs or dropdowns may appear above the overlay if they use higher z-index
   - Ensure consistent z-index management across the application

### Form Submission States
1. **Error Handling**
   - Always reset loading state in error catch blocks
   - Failure to reset `isSubmitting` will leave the overlay visible indefinitely
   - Use try/finally blocks to ensure loading state is always reset

2. **File Upload Tracking**
   - Large file uploads may appear to freeze if no progress indicator is provided
   - Consider implementing more granular file upload progress tracking
   - Upload progress requires proper API endpoint support 

## Unit Profiles Gotchas

### Migration Issues

When implementing the `unit_profiles` table, we encountered several migration challenges:

1. **Index Dependencies**: Several indices in the database are required by foreign key constraints. When Alembic detects a schema difference between the model definition and database (for indexes), attempting to drop these indices causes errors. Always use `if_not_exists=True` when creating tables and comment out index operations that conflict with foreign key constraints.

2. **Database Name Discrepancy**: When working with MariaDB/MySQL, ensure that the connection string in `alembic.ini` matches the actual database name. Migration failures can occur if there's a mismatch between the expected database name and the actual one.

3. **Database Permissions**: The migration user needs appropriate permissions from all possible connection sources. For Docker environments, this might mean granting permissions to both `localhost` and the internal Docker network IPs (e.g., `172.17.0.1`).

4. **PyMySQL Required**: The Flask-SQLAlchemy to MariaDB connection requires the PyMySQL package when using the `mysql+pymysql://` connection string. Ensure this is installed in the virtual environment with `pip install PyMySQL`.

### Data Validation

- The `unit_number` field is a unique identifier and should be validated both on the backend and frontend to ensure consistency.
- When displaying or storing parking/bike storage information that uses comma-separated values, be careful with validation to avoid injection risks.

### Foreign Key Behavior

The `updated_by` foreign key uses `ON DELETE SET NULL` to ensure that if a user is deleted, the unit profile history isn't lost. This means applications should handle potential NULL values in this field.

## Password Reset Gotchas

### Token Security & Handling
- **SECRET_KEY:** The security of `itsdangerous` tokens relies heavily on a strong, secret `SECRET_KEY` in the Flask configuration. Ensure this is properly set and kept confidential, especially in production.
- **Salt:** Using a specific `salt` ('password-reset-salt') isolates these tokens from other potential uses of `itsdangerous`.
- **Expiration:** Tokens correctly expire after 24 hours (`max_age=86400`). Attempts to use expired tokens are rejected.
- **User Enumeration:** The `request-password-reset` endpoint deliberately avoids confirming if an email exists to prevent attackers from discovering valid user emails. It always returns a generic success message.
- **Frontend URL Construction:** Generating the correct absolute URL for the reset link (pointing to the frontend) can be tricky. The current implementation in `auth_routes.py` tries to guess based on the request origin or `BASE_URL` config, but this might need refinement depending on the deployment setup (e.g., different ports, reverse proxies).

### Email Delivery
- **SMTP Configuration:** Email sending relies entirely on the SMTP settings configured in the `Settings` page/database. If these are incorrect or missing, password reset emails will fail silently (though errors are logged).
- **Spam Filters:** Emails containing links, especially password reset links, can sometimes be flagged as spam. Ensure the HTML template is well-formed and consider implementing SPF/DKIM records for the sending domain to improve deliverability.
- **Error Handling:** The `send_password_reset_email` function includes basic error logging but doesn't currently retry or explicitly notify the user/admin of failures beyond the log message.

### Session Invalidation
- **Critical Step:** Terminating all other active sessions (`user.terminate_all_sessions()`) after a successful password reset is a crucial security measure to log out potentially compromised sessions.

### Rate Limiting
- **Storage Backend:** The current implementation uses `memory://` storage for `Flask-Limiter`. This works for single-process development but **will not work correctly** if the application is deployed with multiple worker processes (e.g., using Gunicorn). For production, switch to a shared storage backend like Redis (`storage_uri="redis://localhost:6379"`).
- **Limit Tuning:** The current limits (IP: 10/5min, 50/hr; Email: 3/hr) are starting points. Monitor logs and user feedback to potentially adjust these based on observed traffic patterns and any abuse attempts. 