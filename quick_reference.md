# Quick Reference

This document provides a quick reference for parameters, configuration settings, and common commands.

## Login Form Fields
- **email**: User's email address (required)
- **password**: User's password (required)
- **remember**: Boolean checkbox for persistent login

## React Login Component
Location: `frontend/src/views/auth/Login.js`

### Usage
The login form is implemented as a React component and uses the following fields:
- **email**: User's email address (required)
- **password**: User's password (required)

Example:
```jsx
import Login from './views/auth/Login';
<Login />
```

### Logo Handling
- The login form displays a logo using the path `/logospectrum.png`.
- If the logo fails to load, a base64-encoded fallback image is shown automatically.

## Example Usage
```html
<form method="post">
  {{ form.hidden_tag() }}
  {{ form.email(class="form-control", placeholder="Email") }}
  {{ form.password(class="form-control", placeholder="Password") }}
  {{ form.remember(class="form-check-input") }}
</form>
```

## Configuration
- Static files referenced via `url_for('static', filename='...')`
- Flash messages for error handling

## Dynamic Violation Fields

### Models
- **FieldDefinition**: id, name, label, type, required, options, order, active
- **ViolationFieldValue**: id, violation_id, field_definition_id, value

### API Endpoints
- `GET/POST /api/admin/fields/`: List/create field definitions
- `GET/PUT/DELETE /api/admin/fields/<id>`: Retrieve/update/delete/toggle field
- `POST /api/admin/fields/reorder`: Update order of fields
- `GET/POST /api/violations/`: Accept/return dynamic fields
- `GET/PUT /api/violations/<id>`: Support dynamic field editing

### Example Field Definition (JSON)
```json
{
  "name": "vehicle_make",
  "label": "Vehicle Make",
  "type": "text",
  "required": true,
  "order": 1,
  "active": true
}
```

### Example Violation Submission (JSON)
```json
{
  "date": "2024-06-01",
  "location": "Lot 5",
  "fields": [
    {"field_definition_id": 1, "value": "Toyota"},
    {"field_definition_id": 2, "value": "Red"}
  ]
}
```

## React Component Usage

### AdminFieldManager
```jsx
import AdminFieldManager from './components/AdminFieldManager';
<AdminFieldManager />
```

### DynamicViolationForm
```jsx
import DynamicViolationForm from './components/DynamicViolationForm';
<DynamicViolationForm onSubmit={handleSubmit} initialValues={existingValues} submitLabel="Save" />
```

## API Endpoints (Frontend)
- `GET /api/fields` — List all field definitions
- `POST /api/fields` — Create new field
- `PUT /api/fields/:id` — Update field
- `DELETE /api/fields/:id` — Delete field
- `POST /api/fields/:id/toggle` — Toggle active/inactive
- `POST /api/fields/reorder` — Reorder fields
- `GET /api/violations/:id/fields` — Get field values for a violation

## API: GET /api/violations
- Returns a list of violations.
- Admins: all violations. Users: only their own.
- Each violation: id, reference, category, building, unit_number, incident_date, subject, details, created_at, created_by, dynamic_fields (object).

## React: <ViolationList />
- Fetches and displays violations in a table.
- Shows reference, category, created_at, and all dynamic fields.
- Route: /violations (protected).

## API: GET /api/violations/:id
- Returns details for a single violation (role-protected).
- Admins: any violation. Users: only their own.
- Returns: id, reference, category, building, unit_number, incident_date, subject, details, created_at, created_by, dynamic_fields (object).

## React: <ViolationDetail />
- Fetches and displays details for a single violation.
- Route: /violations/:id (protected).

## API: PUT /api/violations/:id
- Edit a violation (role-protected).
- Body: JSON with any of category, building, unit_number, incident_date, subject, details, dynamic_fields (object).
- Returns: { success: true }

## API: DELETE /api/violations/:id
- Delete a violation (role-protected).
- Returns: { success: true }

## React: <ViolationDetail />
- Edit and delete actions available for admins and owners.
- Edit: Inline form for static and dynamic fields, saves via PUT.
- Delete: Confirms and deletes via DELETE, then redirects.

## React: <Table />
- Reusable table component.
- Props: columns (array of {label, accessor}), data (array), renderCell (optional function).
- Example:
```jsx
<Table columns={[{label: 'Email', accessor: 'email'}]} data={users} />
```

## React: <Modal />
- Reusable modal dialog.
- Props: isOpen, onClose, title, children, actions (optional).
- Example:
```jsx
<Modal isOpen={show} onClose={close} title="Confirm">Are you sure?</Modal>
```

## API: /api/users
- `GET /api/users` — List users (admin only)
- `POST /api/users` — Create user (admin only)
- `PUT /api/users/:id` — Edit user (admin only)
- `DELETE /api/users/:id` — Delete user (admin only, cannot self-delete)
- `POST /api/users/:id/change-password` — Change password (admin or self)

## Quick Reference Guide

## UI Components Quick Reference

### Common Notus React Classes

#### Layout
```css
/* Container */
.container .mx-auto .px-4

/* Card */
.relative .flex .flex-col .min-w-0 .break-words .w-full .mb-6 .shadow-lg .rounded-lg .bg-white .border-0

/* Section */
.px-4 .lg:px-10 .py-10
```

#### Forms
```css
/* Input Field */
.border-0 .px-3 .py-3 .placeholder-blueGray-300 .text-blueGray-600 .bg-white .rounded .text-sm .shadow .focus:outline-none .focus:ring .w-full .ease-linear .transition-all .duration-150

/* Label */
.block .uppercase .text-blueGray-600 .text-xs .font-bold .mb-2

/* Button Primary */
.bg-lightBlue-500 .text-white .active:bg-lightBlue-600 .text-sm .font-bold .uppercase .px-6 .py-3 .rounded .shadow .hover:shadow-lg .outline-none .focus:outline-none .mr-1 .mb-1 .w-full .ease-linear .transition-all .duration-150

/* Button Danger */
.bg-red-500 .text-white .active:bg-red-600 /* Same modifiers as primary */
```

#### Typography
```css
/* Headings */
.text-blueGray-700 .text-xl .font-bold /* Large */
.text-blueGray-600 .text-lg .font-semibold /* Medium */
.text-blueGray-500 .text-sm .font-bold /* Small */

/* Body Text */
.text-blueGray-500 .text-sm /* Regular */
.text-blueGray-400 .text-xs /* Small */
```

#### Navigation
```css
/* Nav Link */
.text-blueGray-700 .hover:text-blueGray-500 .px-3 .py-4 .lg:py-2 .flex .items-center .text-xs .uppercase .font-bold

/* Active Nav Link */
.text-lightBlue-500 .hover:text-lightBlue-600
```

## Error Handling Best Practices

### Database Operations

- **Safe Attribute Access**
  ```python
  # Unsafe
  value = model.attribute
  
  # Safe
  value = getattr(model, 'attribute', default_value)
  ```

- **Attribute Existence Check**
  ```python
  # Check before using
  if hasattr(model, 'attribute'):
      process(model.attribute)
  ```

- **Try/Except for Database Operations**
  ```python
  try:
      result = query.all()
  except Exception as e:
      logger.error(f"Database error: {str(e)}")
      result = []  # Default value
  ```

- **Raw SQL for Schema Stability**
  ```python
  from sqlalchemy import text
  
  # Direct SQL query that only uses known columns
  sql = "SELECT id, name FROM table"
  result = db.session.execute(text(sql))
  ```

### API Response Strategy

- Return sensible defaults instead of errors when possible
- Log errors server-side with sufficient context
- Don't expose internal error details to clients
- Favor empty collections over null values for arrays

## Violation Documents

### HTML and PDF Generation

- HTML and PDF files are automatically generated for each violation
- Both files are stored on the server and referenced in the database

### API Endpoints

- **View HTML**: `/violations/view/{violation_id}`
  - Public route to view a violation's HTML representation
  - Generates the HTML file on-demand if it doesn't exist

- **Download PDF**: `/violations/pdf/{violation_id}`
  - Protected route (requires authentication)
  - Generates the PDF file on-demand if it doesn't exist
  - Returns the file with Content-Disposition: attachment

### Frontend Links

- **Violation Detail View**: 
  - "View as HTML" button
  - "Download PDF" button

- **Violation List**: 
  - HTML link in the Actions column
  - PDF link in the Actions column

- **Dashboard**: 
  - HTML link in the Documents column
  - PDF link in the Documents column

### Database Fields

The Violation model includes:
- `html_path`: String(255) - Path to the HTML file
- `pdf_path`: String(255) - Path to the PDF file

These paths are included in all API responses where violations are listed.

## System Settings

### SMTP Email Configuration
- **Location**: Admin-only page at `/admin/settings`
- **Settings**:
  - SMTP Server (e.g., smtp.gmail.com)
  - SMTP Port (e.g., 587 for TLS)
  - SMTP Username
  - SMTP Password
  - Use TLS/SSL (checkbox)
  - From Email
  - From Name
- **Testing**: Send test emails directly from the settings page

### Global Notification Emails
- **Location**: Admin-only page at `/admin/settings`
- **Format**: Comma-separated list of email addresses
- **Control**: Toggle to enable/disable global notifications
- **Behavior**: When enabled, all violations notifications are sent to these addresses in addition to any violation-specific emails

### API Endpoints
- `GET /api/admin/settings` - Retrieve current settings (admin only)
- `PUT /api/admin/settings` - Update settings (admin only)
- `POST /api/admin/settings/test-email` - Send test email (admin only)

### Settings Model
```python
# Key fields in the Settings model
smtp_server = db.Column(db.String(255))
smtp_port = db.Column(db.Integer)
smtp_username = db.Column(db.String(255))
smtp_password = db.Column(db.String(255))
smtp_use_tls = db.Column(db.Boolean, default=True)
smtp_from_email = db.Column(db.String(255))
smtp_from_name = db.Column(db.String(255))
notification_emails = db.Column(db.Text)  # Comma-separated
enable_global_notifications = db.Column(db.Boolean, default=False)
```

### Example: Using Settings in Code
```python
from app.models import Settings

# Get settings
settings = Settings.get_settings()

# Get list of notification emails
email_list = settings.get_notification_emails_list()
```

## Authentication and User Management

### User Roles
- **Admin**: Full access to all features and violations
- **Manager**: Can manage violations but not users/settings
- **User**: Can only access own violations

## Email Configuration

### SMTP Settings
- **Server**: SMTP server address (e.g., mail.smtp2go.com)
- **Port**: SMTP port (common: 25, 465, 587, 2525)
- **Username**: Authentication username
- **Password**: Authentication password
- **TLS**: Enable for secure connections (recommended)
- **From Email**: Default sender email address
- **From Name**: Optional sender name

### Troubleshooting Commands
```bash
# Check network connectivity to SMTP server
python check_network.py mail.smtp2go.com 2525

# Test SMTP connection with your credentials
python test_smtp_connection.py mail.smtp2go.com 2525 username password

# Test email sending through Flask
python test_flask_email.py recipient@example.com
```

### Common SMTP Ports
- **25**: Standard SMTP (often blocked by ISPs)
- **465**: SMTP over SSL
- **587**: SMTP with STARTTLS
- **2525**: Alternative SMTP port (useful when 25 is blocked)

## Static Violation Fields (2024)

| API Parameter Name                 | Type      | Description                                 |
|------------------------------------|-----------|---------------------------------------------|
| date_of_violation                  | Date      | Date of violation (YYYY-MM-DD)              |
| time                               | String    | Time of violation (HH:MM)                   |
| unit_no                            | String    | Unit number                                 |
| building                           | String    | Building name                               |
| owner_property_manager_first_name   | String    | First name of owner/property manager        |
| owner_property_manager_last_name    | String    | Last name of owner/property manager         |
| owner_property_manager_email        | String    | Email of owner/property manager             |
| owner_property_manager_telephone    | String    | Telephone of owner/property manager         |
| violation_category                  | String    | Violation category                          |
| where_did                          | String    | Location of violation                       |
| was_security_or_police_called       | String    | Security/Police involvement                 |
| fine_levied                        | String    | Fine levied                                 |
| incident_details                    | Text      | Incident details (long text)                |
| action_taken                        | Text      | Action taken                                |
| tenant_first_name                   | String    | Tenant first name                           |
| tenant_last_name                    | String    | Tenant last name                            |
| tenant_email                        | String    | Tenant email                                |
| tenant_phone                        | String    | Tenant phone                                |
| concierge_shift                     | String    | Concierge shift                             |
| noticed_by                          | String    | Who noticed the violation                   |
| people_called                       | String    | People called                               |
| actioned_by                         | String    | Who actioned                                |
| people_involved                     | String    | People involved                             |
| attach_evidence                     | Text/JSON | File metadata/paths                         |
| status                              | String    | Violation status                            |

---

*Update this file as new parameters, configurations, or usage examples are added or changed.* 

Note: The system now uses only static fields and the status field is editable after creation in the violation detail/edit page. 

## Frontend Assets & Branding

- **Login page logo:** `frontend/public/logospectrum.png`
- **To change:** Replace the file and rebuild the frontend. 

## Allowed File Types for Uploads (2024-06)
Uploads are restricted to the following MIME types:
- image/jpeg (.jpg, .jpeg)
- image/png (.png)
- application/pdf (.pdf)
- application/vnd.openxmlformats-officedocument.wordprocessingml.document (.docx)
- application/vnd.openxmlformats-officedocument.spreadsheetml.sheet (.xlsx)
- text/plain (.txt)

Filenames are sanitized and prefixed with a UUID. Files with unsupported or undetectable types are rejected. See implementation_details.md for details. 

## Pagination Parameters (2024-06)
All paginated API endpoints (e.g., /api/violations, /api/users) enforce strict validation:
- Parameters: page (default 1), per_page (default 10), limit (optional, default 10)
- Maximum per_page/limit: 100 (MAX_PAGE_SIZE=100)
- Requests above this return an error. Invalid or missing values default to safe values.
- Error messages are returned for invalid or excessive values. 

## Content Security Policy (CSP) for Generated HTML/PDFs
All generated HTML and PDFs include a restrictive CSP meta tag to prevent XSS:
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; script-src 'none';">
If you need to allow external images or fonts, update the policy in the template. 

## Session Security (2024-06)
- **Session Timeout:** 24 hours (PERMANENT_SESSION_LIFETIME in config.py)
- **Idle Timeout:** 30 minutes (IDLE_TIMEOUT_MINUTES in config.py)
- **Secure Cookies:** SESSION_COOKIE_SECURE, SESSION_COOKIE_HTTPONLY, SESSION_COOKIE_SAMESITE
- **Re-authentication:** Sensitive actions require password re-entry within 5 minutes (@require_recent_password in auth_routes.py) 

## API Endpoints (2024-06)
- `GET /api/violations/public/<uuid:public_id>`: Fetch violation details using public UUID.
- `/evidence/<violation_id>/<filename>`: Securely serve attached evidence files.

## Frontend Routes (2024-06)
- `/violations/public/:publicId`: Violation detail page using public UUID. 

# Recent Quick Reference Updates (June 2024)

## API Authentication
- All sensitive API endpoints now require JWT authentication. Use the `Authorization: Bearer <token>` header for requests.
- User identity is accessed via `get_jwt_identity()` in backend routes.

## Unit API Endpoints
- All unit-related endpoints now require JWT authentication.
- Example: `GET /api/units` (requires JWT)

## UI Button Color Conventions
- Add User: `.bg-lightBlue-500` (blue)
- Edit: `.bg-yellow-500` (yellow)
- Delete: `.bg-red-500` (red)
- Change Password: `.bg-blueGray-500` (gray)

## Unit Profiles List
- Building column removed.
- Added columns: First Name, Last Name, Rented, Has Dog, Has Cat.
- Edit button (yellow) appears next to View.

## Unit Detail Page
- Supports `edit=true` query parameter to enable edit mode directly from the list view.

## Tenant Information
- "Phone" field renamed to "Telephone".
- Telephone validation: 10-digit numbers only. Format guidance is shown below the input.

## Example: Edit Unit Detail via Query Parameter
```
/units/123?edit=true
```

## Example: Telephone Field Validation Message
```
Please enter a 10-digit telephone number (e.g., 6041234567).
```

## User Creation Fields (June 2024)
- **first_name**: User's first name (required)
- **last_name**: User's last name (required)
- **email**: User's email address (required)
- **role**: User's role (admin, user, etc.) (required)
- **position**: User's position (required, dropdown: Council, Property Manager, Caretaker, Cleaner, Concierge)
- **password**: User's password (required)
- **active**: Boolean checkbox for account activation

### Example Add User Payload
```json
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

### UI Field Order (Add User Modal)
1. First Name
2. Last Name
3. Email
4. Role
5. Position (dropdown)
6. Password
7. Active (checkbox)

### Position Dropdown Options
- Council
- Property Manager
- Caretaker
- Cleaner
- Concierge

Validation: All fields above are required for new users. Only the listed positions are accepted. 

## Parameters & Configuration Reference

_List all important parameters, configuration options, and their meanings._

---

## Usage Patterns & Examples

_Provide concise usage examples and command references for common tasks._

---

## Cheatsheet

_Add a cheatsheet for quick lookups of commands, options, or patterns._ 