# Memory Bank — Strata Violation Logging App

This file serves as a persistent, human-readable memory bank for the project. It summarizes project context, architecture, major decisions, and conventions for onboarding and future reference.

---

## Project Overview
- **Name:** Strata Violation Logging App
- **Stack:** Flask, SQLAlchemy, WTForms, Flask-Login, Flask-Mail, WeasyPrint, Bootstrap
- **Purpose:** Log, manage, and report strata violations with robust user/admin controls and modern UI

## Architecture & Decisions
- **Blueprints:** Modular separation for authentication (`auth_routes.py`), violations (`violation_routes.py`), and admin (`admin_routes.py`)
- **Forms:** WTForms for all user input
- **Templates:** All inherit from `base.html` for DRY, consistent UI
- **Config:** Centralized in `config.py`, loaded from environment variables
- **Utilities:** File upload, PDF, email logic in `utils.py`
- **Role-based Access:** `User.is_admin` controls admin privileges
- **Documentation:** Major decisions in `ARCHITECTURE.md`, usage/setup in `README.md`
- **Login Redirect:** Setting `login_manager.login_view = 'auth.login'` fixed the 401/302 redirect test issue, ensuring unauthenticated users are redirected to the login page
- **Test Isolation:** Updated pytest fixture to reset the database between tests using an in-memory SQLite DB. Each test now starts with a clean database state.

## Conventions & Guidelines
- Use blueprints for all new feature modules
- WTForms for all forms and validation
- Update `ARCHITECTURE.md` and this file with major changes
- Write docstrings and comments for all new code

## Persistent Context
- This project is refactored for maintainability, extensibility, and robust access control
- All new developers should review this file, `ARCHITECTURE.md`, and `README.md` before making changes
- Note: Registration test still fails, likely due to duplicate email or test DB state not being reset between tests
- 2025-04-29: Changed Flask development server to run on port 5003 for local testing (previously 5001, originally 5000).
- 2025-04-29: Fixed login, register, and reset password templates by moving form content from block 'container' to block 'content', ensuring forms render as intended.

---

*For updates, add new memories or key decisions below this line:*

---

## [2025-04-29] Application Structure & Implementation Review

### Blueprints
- **auth_routes.py**: Handles authentication (login, logout, registration, password reset).
- **violation_routes.py**: Handles violation CRUD, custom fields, and related admin actions.
- **admin_routes.py**: Handles user management (promote/demote admin).
- **routes.py**: Main dashboard, registration, and password reset (some overlap with auth_routes).

### Models
- **User**: `id`, `email`, `password_hash`, `is_admin` (role-based access).
- **Violation**: Rich schema for violations, including `reference`, `category`, `details`, `extra_fields` (JSON), and metadata for incident and reporting.

### Forms
- **LoginForm, RegisterForm, ResetPasswordForm**: WTForms for authentication.
- **ViolationForm**: WTForms for violation entry, supports dynamic/custom fields.

### Utilities
- **utils.py**: File upload, PDF generation (WeasyPrint), and email (Flask-Mail) helpers.

### Templates
- All templates inherit from `base.html` for consistent UI.
- Custom fields for violations are managed via JSON file and rendered dynamically in forms.

### Other Notes
- Uses Flask-Login for authentication and role-based access control.
- Uses SQLAlchemy ORM for persistence.
- **Production database is MariaDB (see `SQLALCHEMY_DATABASE_URI` in `config.py`). Project was migrated from SQLite to MariaDB for better scalability and production reliability.**
- Admin users can manage custom violation fields and promote/demote users.
- Project is modular and follows best practices for maintainability and extensibility.

### Persistent Context (Update)
- The actual implementation matches the architectural intent described above.
- No evidence of a separate "memory bank" feature for user notes or logs; all persistent data is related to users and violations.
- Custom violation fields are managed via a JSON file and admin interface.
- Test isolation is handled via in-memory SQLite in pytest fixtures.

---

## [2025-05-03] User Identification Enhancements

### Issue Addressed
- Violation details were displaying numeric user IDs (e.g., "Created By: 1") rather than user email addresses, making it difficult to identify who created violations.

### Solution Implemented
- Enhanced API endpoints to include user email addresses alongside user IDs in violation responses:
  - Added creator email lookup to `/api/violations/<id>` endpoint
  - Added creator email lookup to `/api/violations` endpoint for lists
- Updated frontend components to display email addresses instead of IDs:
  - Modified ViolationDetail component to show creator's email
  - Added fallback to "Unknown user" when email is unavailable
- Maintained backward compatibility by preserving original user ID fields

### Technical Implementation
- User lookup is done at the API level, not requiring database schema changes
- Error handling ensures the system works even if user records are deleted
- Documentation updated in `implementation_details.md` and `mental_model.md`

### Benefits
- Improved user experience with human-readable identification
- Enhanced traceability for violation records
- Consistent with existing email-based identification in replies

---

## [2025-05-03] Dashboard Status-Based Counting

### Issue Addressed
- Dashboard was showing all violations as "Active" regardless of their status
- No way to track resolved violations separately from active ones

### Solution Implemented
- Enhanced the dashboard statistics API (`/api/stats`) to count violations based on their Status field value
- Defined specific status values that indicate an active violation:
  - "Open"
  - "Pending Owner Response" 
  - "Pending Council Response"
- Any other status values are counted as resolved violations

### Technical Implementation
- Added Status field check in the `dashboard_routes.py` for each violation
- First finds the Status field definition from FieldDefinition table
- For each violation, checks its corresponding field value
- Categorizes violations as active or resolved based on status value
- Added appropriate error handling to ensure dashboard functions even if database issues occur

### Benefits
- More accurate dashboard statistics
- Better workflow tracking with clear distinction between active and resolved violations
- Foundation for future status-based filtering and reporting

---

## [2025-05-03] Secure URL System Implementation

The system has been enhanced with a comprehensive secure URL implementation:

### Backend Changes
1. Added UUID-based `public_id` to Violation model
2. Created database migration and script to generate UUIDs for existing records
3. Added new API endpoints and routes using `public_id` instead of sequential IDs:
   - `/api/violations/by-public-id/<public_id>`
   - `/violations/view/by-public-id/<public_id>`
   - `/violations/pdf/by-public-id/<public_id>`
4. Implemented cryptographically signed, time-limited tokens for public access
5. Added comprehensive access logging for security auditing

### Frontend Changes
1. Updated React Router with new secure routes:
   - Added `/violations/public/:publicId` route
   - Enhanced ViolationDetail to support both ID types
2. Modified ViolationList to generate secure links
3. Updated NewViolationPage to redirect to UUID-based URLs
4. Enhanced API integration to support both legacy and secure endpoints

### Security Benefits
1. Prevention of ID enumeration attacks
2. Non-sequential, unpredictable identifiers in URLs
3. Temporal decoupling (UUIDs don't reveal creation order)
4. Reduced risk during screen sharing and in browser history
5. Comprehensive security audit trail

### Key Implementation Notes
1. Used `itsdangerous` library for secure token generation
2. Maintained backward compatibility throughout
3. Implemented progressive enhancement rather than breaking change
4. Applied DRY principles by sharing validation logic between endpoints
5. Ensured file access security with multi-layer protection

### Gotchas & Solutions
1. **Issue**: SQLite schema update for existing database
   **Solution**: Created standalone script `update_uuids.py` to add column and generate UUIDs
   
2. **Issue**: Maintaining backward compatibility with existing frontend
   **Solution**: Dual support for both URL types and progressive enhancement
   
3. **Issue**: API responses containing paths needed updates
   **Solution**: Added both path formats in responses for seamless transition

This update significantly enhances system security without disrupting user experience.

---

## System Architecture

- Backend: Flask Python application 
- Frontend: React SPA using Notus design
- Database: SQLite (migrations via Flask-Migrate)
- Authentication: JWT-based session tokens
- PDF Generation: WeasyPrint 
- Email: Flask-Mail with SMTP configuration stored in database
- File Storage: Secure directory structure with virus scanning
- Security: Token-based secure URLs with 24-hour expiration

## Key Implementation Features

### Violation Management
- Full CRUD operations for violation records
- Dynamic field system for customizable forms
- PDF generation with WeasyPrint
- Email notifications for new violations
- Response system for violation feedback
- Secure URL access via cryptographic tokens

### Security System
- User authentication with Flask-Login
- Argon2id password hashing
- UUID-based filenames to prevent enumeration
- ClamAV virus scanning for all file uploads
- Token-based secure URLs with automatic expiration
- Comprehensive access logging
- File storage outside web-accessible directories

### File Management
- UUID-based file naming for security
- Hierarchical storage structure (/saved_files/{html,pdf,uploads})
- ClamAV virus scanning integration
- Secure file serving with proper authentication
- Token-based access for shared files

### Field Definition System
- Admin UI for field management
- Field types: text, select, date, email, file, etc.
- Grid-based layout system
- Field validation rules
- Dynamic form generation

### Dashboard
- Status-based metrics (active, resolved, pending)
- Recent violations listing
- Quick access to common actions
- Performance optimized queries

## Bug History & Solutions

### Bug: File uploads failing silently
- *Problem*: Missing import for `secure_handle_uploaded_file` in violation_routes.py
- *Solution*: Added proper import, ensuring file scanning and UUID-based storage functioned correctly

### Bug: Email notifications not showing correct dynamic fields
- *Problem*: Email templates were using `violation.dynamic_fields` which doesn't exist
- *Solution*: Explicitly queried field values from database and built dynamic_fields dictionary

### Bug: Insecure violation URLs
- *Problem*: Sequential IDs in URLs allowed easy enumeration of all violations
- *Solution*: Implemented UUID-based public_ids and cryptographically signed tokens for all public URLs

### Bug: HTML files not displaying correct dynamic field values
- *Problem*: Template expected `dynamic_fields` but was receiving `field_values`
- *Solution*: Updated `create_violation_html` to correctly pass dynamic_fields to template

## Technical Insights

1. ClamAV virus scanning works best with both Unix and network socket support
2. WeasyPrint may require fallback methods depending on installation environment
3. Secure token generation requires proper configuration of app secret key
4. File access should always be authenticated and logged for security
5. Database schema migrations require careful planning for backward compatibility

## Requirements and Dependencies

- Python 3.11+
- Flask and extensions (flask_sqlalchemy, flask_login, etc.)
- WeasyPrint for PDF generation
- ClamAV and pyclamd for virus scanning
- React 18 for frontend
- itsdangerous for secure token generation
- Argon2 for password hashing

## Database Structure

Key tables:
- users: User accounts and authentication
- violations: Core violation data
- field_definitions: Dynamic field specifications
- violation_field_values: Values for dynamic fields
- violation_replies: Responses to violations
- violation_access_logs: Security logs for all access attempts
- settings: System-wide configuration

## Database Configuration

- **Production database is MariaDB** (see `SQLALCHEMY_DATABASE_URI` in `config.py`). Project was migrated from SQLite to MariaDB for better scalability and production reliability.
- MariaDB connection uses proper connection pooling parameters:
  - `pool_size`: Number of connections to keep in the pool (5 in production, 10 in development)
  - `pool_recycle`: Recycle connections after 30 minutes to prevent stale connections
  - `pool_pre_ping`: Verify connections are still valid before using them
  - `pool_timeout`: Maximum time to wait for a connection from the pool
  - `max_overflow`: Maximum number of connections to create above pool_size
- Robust error handling added for database operations in `app/db_utils.py`:
  - `handle_db_errors`: Decorator for graceful error handling in database operations
  - `safe_commit`: Safely commit changes with error handling
  - `with_transaction`: Transaction handling decorator
  - `check_database_connection`: Connection health check
- Database connection errors are handled gracefully with user-friendly error pages

---

## [2025-05-02] User Identity Enhancement

### Feature Added
- Added first_name and last_name fields to User model
- Updated user forms to collect and display full names
- Modified API endpoints to support first/last name fields
- Enhanced registration process to require first and last names
- Updated session information to include full name data

### Technical Implementation
- Added database columns to users table
- Created migration script for backward compatibility
- Updated all API responses to include name fields
- Modified React components to display full names
- Enhanced API schema to include new identity fields

### Benefits
- Improved user experience with personalized interface
- Enhanced audit trails with clear user attribution 
- More professional communication in violation reports
- Human-readable identification throughout the system
- Better organizational visibility for administration

---
