# Implementation Details

This file contains technical specifics about the Strata Violation Log application, including architecture, dependencies, and implementation notes.

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
- Configuration in `frontend/src/api.js` sets `baseURL: 'http://localhost:5004'`
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

## Violation HTML and PDF Generation

The system automatically generates HTML and PDF files for violations when they are created or updated. This functionality enhances the user experience by providing easy-to-view and downloadable formats of violation records.

### Implementation Details

1. **HTML Generation**
   - When a violation is created or updated, the system calls `create_violation_html()` in `utils.py`
   - This function generates an HTML file using the `violations/detail.html` template
   - The HTML file is stored in the `html_violations` directory
   - The relative path to the HTML file is stored in the `html_path` column of the violation record

2. **PDF Generation**
   - After generating the HTML, the system calls `generate_violation_pdf()` in `utils.py`
   - This function uses WeasyPrint to convert the HTML content to a PDF file
   - If WeasyPrint encounters any issues, fallback mechanisms are in place
   - The PDF file is stored in the `pdf_violations` directory
   - The relative path to the PDF file is stored in the `pdf_path` column of the violation record

3. **Email Notifications**
   - When a violation is created, the system sends email notifications using `send_violation_notification()` in `utils.py`
   - The function looks for email field values in the violation's dynamic fields
   - Instead of attaching large files, the emails include links to view the HTML version and download the PDF
   - This approach reduces email size and prevents email delivery issues

4. **Accessing Documents**
   - HTML files can be viewed at: `/violations/view/{violation_id}`
   - PDF files can be downloaded at: `/violations/pdf/{violation_id}`
   - Both endpoints handle generating the files on-demand if they don't exist

### Frontend Integration

The frontend displays HTML and PDF document links in three places:
1. **Violation Detail View**: Buttons to view HTML and download PDF
2. **Violation List View**: HTML and PDF links in the actions column
3. **Dashboard**: Document links in the recent violations table

### Search and Accessibility

- PDF and HTML paths are included in all violation API responses
- This makes the documents searchable and accessible from any view that lists violations
- Links are stored as relative paths but rendered as absolute URLs in the frontend

### Database Schema

The Violation model includes these fields for document storage:
```
html_path = db.Column(db.String(255))  # Path to the generated HTML file
pdf_path = db.Column(db.String(255))   # Path to the generated PDF file
```

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

---

*Update this file with new technical insights, optimizations, or architectural changes as they arise.* 