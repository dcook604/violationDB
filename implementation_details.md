# Implementation Details

This document details the technical specifics, implementation decisions, and rationale behind the codebase.

## Architecture
- Flask-based web application
- Jinja2 templating for HTML rendering (e.g., `login.html`)
- Static assets (CSS, JS) served via Flask's static route

## Key Files
- `app/templates/login.html`: Login page template
- `app/static/login.css`: Login page styles

## Dependencies
- Flask
- Jinja2
- WTForms (for form handling)

## Implementation Notes
- Login form uses Flask-WTF for CSRF protection and validation.
- Flash messages are used to display errors.
- Inline SVG is used for branding on the login page.

## Dynamic Violation Fields Implementation

### Backend
- **Models:**
  - `FieldDefinition`: Stores metadata for each custom field (name, label, type, required, options, order, active, etc.).
  - `ViolationFieldValue`: Stores values for each violation/field instance (violation_id, field_definition_id, value).
- **API Endpoints:**
  - `/api/admin/fields/` (GET, POST): List/create field definitions
  - `/api/admin/fields/<id>` (GET, PUT, DELETE): Retrieve/update/delete/toggle field
  - `/api/admin/fields/reorder` (POST): Update order of fields
  - `/api/violations/` (GET, POST): Accept/return dynamic fields
  - `/api/violations/<id>` (GET, PUT): Support dynamic field editing
- **Validation:**
  - Field validation enforced based on definition (type, required, etc.)
- **Migrations:**
  - Alembic scripts for new/modified tables

### Frontend
- **Admin UI:**
  - Manage field definitions (list, add, edit, toggle, reorder, preview)
- **Dynamic Form Generator:**
  - Renders form inputs based on field definitions
  - Handles validation and editing
- **Violation Views:**
  - Display dynamic fields in violation details and lists

### Security
- Admin endpoints require authentication and proper authorization.

## React Frontend (Dynamic Violation Fields)

### Structure
- `frontend/src/api.js`: Axios API utility for Flask backend integration
- `frontend/src/components/AdminFieldManager.js`: Admin UI for CRUD, reorder, and toggle of field definitions
- `frontend/src/components/DynamicViolationForm.js`: Dynamic form generator for violations (add/edit)

### Supported Field Types
The system supports the following dynamic field types:
- **text**: Standard text input for general use
- **email**: Email input with validation
- **number**: Numeric input with validation
- **date**: Date picker input
- **time**: Time picker input
- **select**: Dropdown selection with configurable options
- **file**: File upload with configurable size and count limitations

Each field type has appropriate validation and is rendered with the correct HTML input element in the dynamic form.

### API Integration
- All field management and dynamic form features use `/api/fields` and related endpoints from the Flask backend
- Axios is used for HTTP requests; base URL is set via environment variable or defaults to `http://localhost:5000`

### Main Components
- **AdminFieldManager**: Lists, adds, edits, deletes, toggles, and reorders custom fields. Uses `react-beautiful-dnd` for drag-and-drop.
- **DynamicViolationForm**: Fetches field definitions, renders appropriate inputs, validates, and submits values for violations.

### Usage
- Admins access the field manager to configure violation fields
- Users see dynamic forms for violations based on current field definitions

### /api/violations endpoint
- Added to app/violation_routes.py.
- Returns all violations for admins, only user's own for regular users (uses current_user).
- Each violation includes dynamic fields as a nested object (field name -> value).
- Used for React SPA integration.

### ViolationList React component
- Fetches /api/violations on mount.
- Dynamically generates table columns for all dynamic fields present in any violation.
- Uses Notus React/Tailwind for styling.
- Handles loading, error, and empty states.

### /api/violations/:id endpoint
- Added to app/violation_routes.py.
- Returns all details for a single violation, including dynamic fields.
- Role-based: admin can view any, user can only view their own.

### ViolationDetail React component
- Fetches /api/violations/:id on mount (uses useParams for id).
- Displays all static and dynamic fields in a styled card.
- Handles loading, error, and forbidden states.

### /api/violations/:id (PUT, DELETE)
- PUT: Updates static and dynamic fields. Only admin or owner can edit.
- DELETE: Deletes violation and its dynamic fields. Only admin or owner can delete.

### ViolationDetail edit/delete UI
- Shows Edit and Delete buttons if user is admin or owner.
- Edit: Shows inline form, updates via PUT, refreshes on save.
- Delete: Confirms, deletes via DELETE, redirects to /violations.

## Frontend Implementation

### UI Framework and Theming
- The application uses Notus React theme for consistent and professional UI/UX
- Theme configuration is managed through Tailwind CSS
- All components follow Notus React design patterns and styling guidelines

### Theme Components and Styling
- Base styles are defined in `frontend/src/assets/styles/index.css`
- Tailwind configuration in `frontend/tailwind.config.js`
- Color scheme uses blueGray and lightBlue palettes
- Components use consistent spacing, shadows, and transitions

### Component Guidelines
When creating new components or modifying existing ones:
1. Follow Notus React class naming conventions
2. Use predefined color schemes (blueGray, lightBlue)
3. Maintain consistent spacing and typography
4. Include proper transitions and hover states
5. Ensure responsive design patterns

### Common Component Classes
```css
/* Buttons */
.bg-lightBlue-500 /* Primary button background */
.text-white /* Button text */
.active:bg-lightBlue-600 /* Active state */
.shadow hover:shadow-lg /* Button shadow effects */

/* Forms */
.border-0 /* Clean input style */
.shadow /* Input shadow */
.focus:outline-none focus:ring /* Focus states */
.placeholder-blueGray-300 /* Placeholder text */

/* Typography */
.text-blueGray-600 /* Main text color */
.text-blueGray-500 /* Secondary text */
.font-bold /* Bold text */
.uppercase /* Uppercase text */
```

### Login Component (React SPA)
The login page is now implemented as a React SPA component in `frontend/src/views/auth/Login.js`.

- Uses React hooks (`useState`) for managing form state and error messages.
- Integrates with `AuthContext` for authentication logic (`login`).
- Utilizes `useNavigate` from `react-router-dom` for navigation after login.
- Displays a logo with a base64 fallback for branding and reliability.
- Handles error display and form validation (email and password required).
- All authentication is handled via API calls to the backend; the Flask/Jinja2 login template is no longer used for user login.

### File Upload Security (2024-06)
All uploaded files are now subject to strict filename sanitization and content type validation:

- Filenames are sanitized using `werkzeug.utils.secure_filename` and prefixed with a UUID to prevent path traversal and collisions.
- Only the following MIME types are allowed for uploads:
  - image/jpeg (.jpg, .jpeg)
  - image/png (.png)
  - application/pdf (.pdf)
  - application/vnd.openxmlformats-officedocument.wordprocessingml.document (.docx)
  - application/vnd.openxmlformats-officedocument.spreadsheetml.sheet (.xlsx)
  - text/plain (.txt)
- MIME type is detected using `python-magic` if available, otherwise falls back to the browser-provided `file.mimetype`.
- Files with disallowed or undetectable types are rejected and deleted.
- All files are scanned for viruses using ClamAV before being accepted.

## API Error Handling Patterns

### Database Schema Protection

We've implemented defensive coding patterns throughout the API to handle potential database schema inconsistencies. Here are the key patterns used:

1. **Dashboard Stats API (`/api/stats`)**
   - Uses direct SQL queries instead of ORM to avoid column mapping issues
   - Returns default values (zeros) when errors occur instead of 500 status codes
   - Includes try/except blocks to catch and log database errors

2. **Violations List API (`/api/violations`)**
   - Uses direct SQL queries that explicitly name columns known to exist
   - Handles the `limit` parameter properly for pagination
   - Returns empty arrays instead of error codes when database errors occur
   - Includes null-safe access for all returned fields

3. **Error Response Strategy**
   - Log detailed errors on the server side
   - Return user-friendly responses that won't break the UI
   - Use appropriate HTTP status codes for client-side errors, but avoid exposing internal errors

These patterns help maintain application stability even when the database schema doesn't perfectly match the ORM models. This is particularly important during development and after schema migrations.

## API Configuration and Server Management

### API Client Setup
- The frontend API client uses a direct connection to the backend server on port 5004
- Configuration in `frontend/src/api.js` sets `baseURL: 'http://172.16.16.6:5004'`
- All API requests include credentials (`withCredentials: true`) for cookie-based authentication
- Comprehensive error handling for different response scenarios (redirects, unauthorized, network errors)

### Server Management
- Both frontend and backend use fixed ports:
  - Flask backend: Port 5004
  - React frontend: Port 3001
- A reset script (`reset_servers.sh`) provides automated server management:
  - Stops any existing processes on these ports
  - Cleans up stray processes
  - Starts both servers with proper logging
  - Verifies the backend is accessible

### CORS Configuration
- The backend CORS settings allow credentials and specific origins
- Flask app has custom session interface with `SameSite=Lax` for cookie security
- All authentication endpoints support OPTIONS requests for preflight CORS checks

### Authentication Flow
- Session check: `/api/auth/session` endpoint validates current authentication status
- Login: `/api/auth/login` accepts user credentials and sets session cookies
- Logout: `/api/auth/logout` clears session data
- All endpoints return consistent JSON responses and proper HTTP status codes

### Proxy Configuration
- During development, the frontend uses `setupProxy.js` to proxy API requests to the backend
- The proxy preserves paths, handles cookies, and supports cross-origin requests
- Alternatively, direct connections can be used by setting `baseURL` in the API client
- Both approaches ensure proper cookie handling for authentication

## Secure File Handling and Virus Scanning

The system implements a comprehensive secure file handling system with integrated virus scanning:

### Secure Directory Structure

Files are stored in a hierarchical structure outside the web-accessible directories:

```
/home/violation/
├── app/
├── saved_files/         # Secure root storage directory
│   ├── html/            # Generated HTML documents
│   ├── pdf/             # Generated PDF documents
│   └── uploads/         # User-uploaded files
│       └── fields/      # Dynamic field file uploads by violation ID
└── ...
```

### UUID-Based Filenames

All files are stored using UUID-based filenames to prevent enumeration and guessing attacks:

- Format: `{uuid4}_{violation_id}.{extension}`
- Example: `d8e8fca2-dc17-4f31-8a46-920e6e1bbc84_42.pdf`

### ClamAV Virus Scanning Integration

The application integrates ClamAV for virus scanning of all uploaded files:

1. **System Dependencies**:
   - ClamAV daemon (clamav-daemon)
   - ClamAV libraries (libclamav-dev)
   - Updated virus definitions (via freshclam)
   - Python pyclamd module

2. **Scanning Process**:
   - All uploads are scanned before being stored permanently
   - Files with detected viruses are automatically deleted
   - Multiple connection methods (Unix socket and network socket) ensure compatibility

3. **Implementation Flow**:
   - `init_clamav()` establishes connection to the ClamAV daemon
   - `scan_file()` performs the virus scan on a given file path
   - `secure_handle_uploaded_file()` orchestrates the secure upload process with scanning

### Access Control

The system implements strict access control for file operations:

1. **Authentication**: Required for all file access via `@login_required`
2. **Authorization**: Verification of violation ownership or admin role
3. **Path Validation**: Secure path handling to prevent directory traversal
4. **Secure Serving**: `send_from_directory()` for controlled file access

## Violation HTML and PDF Generation

The system automatically generates HTML and PDF files for violations:

### HTML Generation Process

When a violation is created or updated, the system automatically:

1. Collects all field data, including dynamic fields
2. Organizes data for proper template rendering
3. Generates a unique UUID-based filename
4. Creates an HTML document with the violation details
5. Stores the file in the secure `/saved_files/html/` directory

### PDF Generation Process

After HTML generation, the system:

1. Uses the HTML content to generate a PDF version
2. Implements multiple generation methods with WeasyPrint
3. Includes fallback mechanisms for compatibility
4. Stores the PDF file in the secure `/saved_files/pdf/` directory 

### Attached Images Display

The system now properly displays attached images in the violation details:

1. Images attached to fields are organized by field name
2. File paths are converted to proper URLs for the templates
3. Images are displayed in a responsive grid layout
4. Original filenames are shown beneath each image

### Email Notifications

Email notifications have been improved to:

1. Display correct dynamic field values including Category and Details
2. Generate proper links to HTML and PDF versions
3. Include context-appropriate information for recipients
4. Provide a consistent user experience across email clients

## Violation Reply System

The system allows recipients to reply to violations via the web interface:

1. **Reply Form**: Integrated in the HTML view for easy response
2. **Email Notifications**: Sent to violation creators and administrators 
3. **Display**: Responses shown chronologically in the violation detail
4. **Document Updates**: HTML and PDF regenerated to include new replies

## System Settings and Email Configuration

The application includes a settings management system to allow administrators to configure email settings and global notification preferences without modifying code or environment variables.

### Settings Model

The database includes a `Settings` table with the following key fields:

1. **SMTP Configuration**
   - `smtp_server`: The SMTP server hostname (e.g., smtp.gmail.com)
   - `smtp_port`: The SMTP server port (e.g., 587 for TLS)
   - `smtp_username`: SMTP account username
   - `smtp_password`: SMTP account password (stored as plain text)
   - `smtp_use_tls`: Whether to use TLS/SSL for email sending
   - `smtp_from_email`: The default sender email address
   - `smtp_from_name`: The default sender name

2. **Notification Settings**
   - `notification_emails`: Comma-separated list of email addresses to receive all violation notifications
   - `enable_global_notifications`: Whether to send global notifications for all violations

### Dynamic Email Configuration

The email sending system has been enhanced to check the database for SMTP settings before defaulting to the environment configuration:

1. When sending an email, the system first retrieves settings from the database
2. If SMTP server settings exist in the database, they temporarily override the application config
3. After sending the email, the original configuration is restored
4. If no database settings exist, the application falls back to environment variables

### Global Notifications

In addition to sending notification emails to addresses specified in the violation's email fields, the system now supports global notifications:

1. If global notifications are enabled, all violations send notifications to the specified global email addresses
2. These addresses are added to any violation-specific email addresses
3. Duplicate email addresses are automatically removed
4. This feature ensures that designated staff always receive all violation notifications

### Admin Interface

The settings are managed through a dedicated admin interface:

1. **Settings Page**: `/admin/settings` - Only accessible to admin users
2. **Test Email Feature**: Allows admins to verify email configuration by sending a test email
3. **Form Validation**: Validates SMTP settings for format and completeness
4. **Security**: Password field allows leaving the password unchanged if no new value is provided

### Implementation Notes

- Settings are stored in a singleton pattern (only one settings record exists)
- The `get_settings()` class method ensures a default settings record is created if none exists
- Email password is stored in plain text in the database, so database security is critical
- The application dynamically modifies its mail configuration at runtime without requiring a restart

## SMTP Configuration and Email Handling

### Dynamic SMTP Configuration

The application implements a dynamic SMTP configuration system that allows email settings to be updated without requiring application restarts:

- **Database-Stored Settings**: All SMTP settings (server, port, username, password, TLS, sender details) are stored in the `Settings` table in the database.

- **Two-Level Configuration Approach**:
  1. **Application Startup**: SMTP settings are loaded from the database into Flask mail configuration during app initialization in `app/__init__.py`.
  2. **Per-Email Dynamic Loading**: The `send_email` function in `app/utils.py` dynamically loads current SMTP settings from the database for each email operation.

- **Implementation Details**:
  - Each email send operation temporarily modifies the app's mail configuration with current database settings
  - Original configuration is restored after each email operation
  - Connection testing is performed before sending to validate SMTP server availability
  - Comprehensive logging tracks email operations and any failures

### Email Sending Process

1. When `send_email` is called, it immediately fetches current settings from the database
2. The function performs socket connection testing to verify SMTP server availability
3. Flask's mail configuration is temporarily updated with database settings
4. The email message is created and sent via Flask-Mail
5. Original mail configuration is restored, regardless of success or failure
6. All steps are logged for debugging and auditing

### Error Handling

- Socket connection failures trigger detailed error messages
- Missing SMTP settings are clearly reported with specific missing fields
- All errors are logged to help diagnose configuration issues
- Original mail configuration is always restored to prevent configuration corruption

### Security Considerations

- SMTP passwords are stored as plain text in the database (security limitation)
- Database should be properly secured to protect sensitive credentials
- TLS is enabled by default for secure connections
- Debug logs are designed to mask sensitive information

## Secure Violation Access System

The application implements a comprehensive secure URL system for accessing violations:

### UUID-Based Identifiers

Instead of exposing sequential IDs in URLs, each violation now has:

1. An internal ID (used in the database)
2. A UUID-based `public_id` (36-character unique identifier)

This prevents attackers from easily enumerating all violations by incrementing numeric IDs.

### Cryptographically Signed Tokens

All public access to violation details uses signed, time-limited tokens:

1. **Token Generation**: Tokens are created using the `itsdangerous` library with the application's secret key
2. **Token Contents**: Each token contains the violation ID and creation timestamp
3. **Token Expiration**: Tokens automatically expire after 24 hours
4. **Validation Process**: All tokens are validated before granting access

### Comprehensive Access Logging

Every access attempt to violation details is logged for security auditing:

1. **Access Logs Table**: The `ViolationAccess` model tracks all access attempts
2. **Logged Data**: IP address, user agent, timestamp, and token used
3. **Relationship**: Each log entry is linked to the specific violation 
4. **Failed Attempts**: Invalid or expired tokens are logged with warnings

### Secure Routes Implementation

New secure routes have been added for public access:

1. **HTML View**: `/violations/secure/<token>` - Token-authenticated access to HTML view
2. **PDF Download**: `/violations/secure/<token>/pdf` - Token-authenticated PDF download
3. **Email Integration**: All email notifications use secure token URLs

### Security Benefits

This implementation provides several key security benefits:

1. **Prevents Enumeration**: No sequential IDs in URLs
2. **Time-Limited Access**: Tokens expire after 24 hours
3. **Audit Trail**: All access attempts are logged
4. **Cryptographic Security**: Tokens are signed with the application's secret key
5. **No Persistent Access**: Each access requires a valid token

## Frontend URL Security Implementation

To complement the backend secure URL system with UUIDs and cryptographic tokens, the frontend has been updated to use these secure identifiers in all URLs:

### React Router Integration

1. **Dual URL Routes**: The application supports both formats for backward compatibility:
   - Legacy route: `/violations/:id` (numeric ID)
   - Secure route: `/violations/public/:publicId` (UUID-based)

2. **Route Component Enhancement**:
   ```jsx
   <Route path="/violations/public/:publicId" element={
     <PrivateRoute>
       <Layout>
         <ViolationDetail usePublicId={true} />
       </Layout>
     </PrivateRoute>
   } />
   ```

3. **New Violation Redirection**: When creating a new violation, the application now redirects to the UUID-based URL:
   ```jsx
   if (response.data && response.data.public_id) {
     navigate(`/violations/public/${response.data.public_id}`);
   }
   ```

### Components Adaptation

1. **ViolationDetail Component**:
   - Enhanced to support both URL types with a `usePublicId` flag
   - Dynamically selects the appropriate API endpoint based on the URL type
   - Maintains backward compatibility for existing bookmarked URLs

2. **ViolationList Component**:
   - Updated to generate links using public_id when available
   - Presents consistent UI while using secure URLs in navigation
   - Preserves table formatting and pagination with added security

3. **API Integration**:
   - Frontend requests appropriate endpoints based on URL type
   - File links (HTML/PDF) use secure URL patterns when available
   - All requests maintain authenticated state with proper credentials

### Security Benefits for Frontend

1. **No Sequential IDs in Browser History**: URLs stored in browser history and bookmarks no longer expose sequential IDs
2. **Referrer Protection**: When navigating from violation pages, the UUID in the referrer header doesn't leak sequential IDs
3. **Screen Sharing Safety**: During screen sharing, UUID-based URLs don't reveal the sequential structure of data
4. **Temporal Decoupling**: UUIDs provide no indication of the creation order or total number of records

This implementation ensures that the entire application uses secure, unpredictable identifiers in all user-facing URLs while maintaining full backward compatibility.

## User Management System

### User Model
The system uses a comprehensive User model to store and manage user accounts:

- **Core Identity**: 
  - `id`: Primary key
  - `email`: Unique email address (used for login)
  - `first_name`: User's first name
  - `last_name`: User's last name
  - `password_hash`: Secured with Argon2id

- **Access Control**:
  - `is_admin`: Boolean flag for admin privileges
  - `is_active`: Boolean flag for account activation
  - `role`: String role value (user, manager, admin)

- **Security Features**:
  - Argon2id password hashing with time and memory parameters
  - Account lockout after 10 failed attempts
  - Temporary password functionality for resets
  - Session tracking with idle and absolute timeouts

## StaticViolationForm Implementation (2024 Migration)

### Field Structure
The static violation form includes the following fields:
- Date of Violation (date, required)
- Time (time, required)
- Unit No. (number, required)
- Building (dropdown: Townhouse, Apartment, required)
- Owner/Property Manager Name (first, last, required)
- Owner/Property Manager Email (email, required)
- Owner/Property Manager Telephone (phone, required)
- Violation Category (dropdown, required)
- Where did this violation happen? (dropdown, required)
- Was Security or Police called? (dropdown, required)
- Fine Levied (dropdown, required)
- Incident Details (textarea, required)
- Action Taken (textarea, required)
- Tenant Name (first, last, optional)
- Tenant Email (email, optional)
- Tenant Phone (phone, optional)
- Concierge Shift (text, optional)
- Noticed By (text, optional)
- People Called (text, optional)
- Actioned By (text, optional)
- People Involved (textarea, optional)
- Attach Evidence (file upload, multiple, optional)

### Validation
- All required fields are enforced on the client and server.
- Email and phone fields use format validation.
- Dropdowns only accept the specified options.
- File uploads are limited by type, size, and count.

### Backend/API Changes
- The violation creation endpoint now expects only the above static fields.
- Dynamic field logic is deprecated but legacy data remains accessible.
- File uploads are handled as part of the static form submission.

### Example API Payload
```
{
  "date_of_violation": "2024-06-01",
  "time": "14:30",
  "unit_no": "101",
  "building": "Apartment",
  "owner_property_manager_name": {"first": "Jane", "last": "Doe"},
  "owner_property_manager_email": "jane@example.com",
  "owner_property_manager_telephone": "(555) 123-4567",
  "violation_category": "Noise Complaint",
  "where_did": "Unit",
  "was_security_or_police_called": "Security",
  "fine_levied": "$100.00",
  "incident_details": "Loud noise reported at 2:30pm.",
  "action_taken": "Warning issued.",
  "tenant_name": {"first": "John", "last": "Smith"},
  "tenant_email": "john@example.com",
  "tenant_phone": "(555) 987-6543",
  "concierge_shift": "Evening",
  "noticed_by": "Concierge",
  "people_called": "Security",
  "actioned_by": "Manager",
  "people_involved": "John Smith, Jane Doe",
  "attach_evidence": [/* file objects */]
}
```

### 2024 Update: StaticViolationForm Integration

- The `DynamicViolationForm` component has been fully replaced by `StaticViolationForm` in the violation creation workflow (`/violations/new`).
- All new violations are now created using the static, hardcoded field structure.
- The parent page (`NewViolationPage` in `App.js`) now imports and renders `StaticViolationForm`, passing the required `onSubmit` handler and label.
- File uploads and validation are handled internally by the new component.
- This change improves maintainability and ensures all new violations conform to the updated schema.

- 2024-06: Form optimization for StaticViolationForm:
  - Grouped required violation details at the top, followed by owner/manager info, tenant info, other details, then incident details, action taken, file upload, and submit.
  - Added section headings for clarity.
  - Added aria-labels and htmlFor for accessibility.
  - Implemented scroll-to-first-error on submit for better UX.
  - Improved mobile responsiveness and visual hierarchy.

- 2024-06: The 'Create New Violation' heading was removed from the static violation form page (`/violations/new`) for a cleaner UI, as per user request.

- 2024-06: Owner/Property Manager Telephone and Tenant Phone fields are now left-aligned directly under their respective name fields for improved clarity and compactness.

- 2024-06: Police Report No. field removed from the static violation form for clarity and simplicity.

- 2024-06: Added 'status' field to violations.
  - Options: Open, Closed-No Fine Issued, Closed-Fines Issued, Pending Owner Response, Pending Council Response, Reject.
  - Default: 'Open' on creation. Dropdown is disabled on create, editable on edit.
  - All users can change status after creation.
  - Backend: Requires new DB column, API support, and a status change log (violation_status_log table: violation_id, old_status, new_status, changed_by, timestamp).
  - Status changes are logged for audit/history.

- 2024-06: Removed all dynamic field management and AdminFieldManager. The system now uses only static fields for violations. The field manager UI and related backend endpoints/models have been removed. Status is now editable in the violation detail/edit page for all users, and all status changes are logged for audit/history.

# Static Violation Field Expansion (2024)

## New Violation Model Fields
The following fields have been added to the `Violation` model and database as of June 2024:

| Field Name                        | Type    | Description                                 |
|-----------------------------------|---------|---------------------------------------------|
| owner_property_manager_first_name | String  | First name of owner/property manager        |
| owner_property_manager_last_name  | String  | Last name of owner/property manager         |
| owner_property_manager_email      | String  | Email of owner/property manager             |
| owner_property_manager_telephone  | String  | Telephone of owner/property manager         |
| where_did                         | String  | Location of violation                       |
| was_security_or_police_called     | String  | Security/Police involvement                 |
| fine_levied                       | String  | Fine levied                                 |
| action_taken                      | Text    | Action taken                                |
| tenant_first_name                 | String  | Tenant first name                           |
| tenant_last_name                  | String  | Tenant last name                            |
| tenant_email                      | String  | Tenant email                                |
| tenant_phone                      | String  | Tenant phone                                |
| concierge_shift                   | String  | Concierge shift                             |
| noticed_by                        | String  | Who noticed the violation                   |
| people_called                     | String  | People called                               |
| actioned_by                       | String  | Who actioned                                |
| people_involved                   | String  | People involved                             |
| incident_details                  | Text    | Incident details (long text)                |
| attach_evidence                   | Text/JSON | File metadata/paths (see below)           |

- All fields are nullable except where required by the frontend form.
- `attach_evidence` stores file metadata/paths as a JSON-encoded string or text.

## Alembic Migration
A migration script is required to add these columns to the `violations` table. See the migrations directory for details.

## API Payload Example (2024)
```
{
  "date_of_violation": "2024-06-01",
  "time": "14:30",
  "unit_no": "101",
  "building": "Apartment",
  "owner_property_manager_first_name": "Jane",
  "owner_property_manager_last_name": "Doe",
  "owner_property_manager_email": "jane@example.com",
  "owner_property_manager_telephone": "(555) 123-4567",
  "violation_category": "Noise Complaint",
  "where_did": "Unit",
  "was_security_or_police_called": "Security",
  "fine_levied": "$100.00",
  "incident_details": "Loud noise reported at 2:30pm.",
  "action_taken": "Warning issued.",
  "tenant_first_name": "John",
  "tenant_last_name": "Smith",
  "tenant_email": "john@example.com",
  "tenant_phone": "(555) 987-6543",
  "concierge_shift": "Evening",
  "noticed_by": "Concierge",
  "people_called": "Security",
  "actioned_by": "Manager",
  "people_involved": "John Smith, Jane Doe",
  "attach_evidence": [/* file objects or metadata */],
  "status": "Open"
}
```

## Validation
- All required fields are enforced on both client and server.
- Email and phone fields use format validation.
- Dropdowns only accept the specified options.
- File uploads are limited by type, size, and count.

## Authentication UI and Branding

- The login page imports and displays the Spectrum 4 logo from `/logospectrum.png` (in the public directory).
- CSS ensures the logo is centered, visually separated, and works with both light and dark themes.
- If the logo fails to load, a fallback is shown.

## Pagination and Filtering Security (2024-06)
All API endpoints that support pagination or filtering parameters (e.g., page, per_page, limit) now enforce strict validation:

- All pagination parameters are validated as integers and must be within allowed ranges.
- The maximum allowed value for per_page or limit is 100 (MAX_PAGE_SIZE=100). Requests above this return an error.
- Invalid or missing parameters default to safe values (page=1, per_page=10).
- This prevents abuse and denial-of-service by requesting excessively large result sets.
- Endpoints affected: /api/violations, /api/users (and any future paginated endpoints).

## Content Security Policy for Generated HTML/PDFs (2024-06)
All generated HTML (and thus PDFs) now include a restrictive Content Security Policy (CSP) meta tag in the <head>:

<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; script-src 'none';">

This policy blocks all scripts, restricts images to self and data URIs, and only allows inline styles and self-hosted fonts. This helps prevent XSS in violation detail views and exported PDFs.

## Session Security Improvements (2024-06)
#### Session Timeout and Idle Timeout
- User sessions now expire after 24 hours (absolute timeout) or 30 minutes of inactivity (idle timeout).
- Enforced via a before_app_request handler in auth_routes.py.
- Users are logged out and redirected to login if their session expires.

#### Secure Cookie Settings
- SESSION_COOKIE_SECURE, SESSION_COOKIE_HTTPONLY, and SESSION_COOKIE_SAMESITE are set for all environments (production must use HTTPS).

#### Re-authentication for Sensitive Actions
- A @require_recent_password decorator is available for sensitive endpoints (e.g., change password, admin actions).
- Requires password re-entry within the last 5 minutes.
- Usage: see auth_routes.py for example.

## Violation Detail Page Enhancements (2024-06)
Uses UUID-based URLs (`/violations/public/:publicId`) for enhanced security and obscurity.
Displays all static violation fields correctly.
Renders attached evidence files (images/links).
Action buttons (View HTML, Download PDF, Edit, Delete) are arranged on a single line.
Delete button is styled red for visual warning.
Includes a "Go Back" link to the violations list.

# Recent Implementation Details (June 2024)

## CORS and Authentication
- CORS allowed origins updated to include 172.16.16.6 and 172.16.16.26, resolving cross-origin issues for frontend-backend communication.
- All API endpoints requiring authentication now use `@jwt_required_api` instead of `@login_required` for SPA compatibility and stateless session management.
- User identity is accessed via `get_jwt_identity()` in API routes, replacing `current_user.id` for JWT-based flows.

## Form and Validation Updates
- Unit creation form: Unit number field is now enabled for new units.
- Tenant information: "Phone" field renamed to "Telephone"; validation updated to require 10-digit numbers. Format guidance is displayed below the input.

## UI/UX Enhancements
- User Management: Button color conventions standardized (Add User: blue, Edit: yellow, Delete: red, Change Password: gray).
- Unit Profiles: Building column removed; First Name, Last Name, Rented, Has Dog, Has Cat indicators added; Edit button (yellow) appears next to View.
- Unit detail page now supports `edit=true` query parameter to enable direct edit mode from the list view.

## API Endpoint Changes
- All unit-related API endpoints now require JWT authentication and use `get_jwt_identity()` for user context.
- Example: In `unit_routes.py`, all `@login_required` decorators replaced with `@jwt_required_api`.

## Rationale
- These changes improve security, maintain SPA compatibility, and enhance user experience while maintaining backward compatibility.

## User Creation: First/Last Name and Position (June 2024)
- The Add User modal now includes required First Name and Last Name fields above Email.
- A required Position dropdown is added below Role, with options: Council, Property Manager, Caretaker, Cleaner, Concierge.
- Backend user creation API updated to accept and store `first_name`, `last_name`, and `position`.
- Validation ensures all fields are present; error messages are shown for missing/invalid input.
- User management UI displays these fields for all users.
- Example API payload:
```
{
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane@example.com",
  "role": "user",
  "position": "Caretaker",
  "password": "changeme123",
  "active": true
}
```

---

*Update this file with new technical insights, optimizations, or architectural changes as they arise.* 