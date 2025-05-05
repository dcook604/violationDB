# User Management Quick Reference

## User Roles
| Role    | Access Level | Permissions                    |
|---------|-------------|--------------------------------|
| user    | Basic       | Access own account             |
| manager | Extended    | View/manage violations         |
| admin   | Full        | Full system administration     |

## API Methods Quick Reference

### User Creation
```python
# Create new user
user = User(email="user@example.com", role="user")
user.set_temporary_password()  # Returns temporary password

# Generate temporary password
temp_pass = User.generate_temp_password()
```

### Role Management
```python
# Set user role
user.set_role('manager')  # Options: 'user', 'manager', 'admin'

# Promote to admin
user.promote_to_admin()  # Sets role='admin' and is_admin=True

# Activate user
user.activate(is_admin=False)  # Optional admin promotion
```

### Password Management
```python
# Set temporary password
temp_pass = user.set_temporary_password(expiry_hours=24)

# Check temporary password
is_valid = user.check_temporary_password(password)

# Clear temporary password
user.clear_temporary_password()
```

## Common Operations

### User Creation
```python
# Admin creates new user
temp_password = User.generate_temp_password()
user = User(
    email=email,
    password_hash=generate_password_hash(temp_password),
    role=role,
    is_active=True
)
db.session.add(user)
db.session.commit()
```

### Password Reset
```python
# Admin resets user password
temp_pass = user.set_temporary_password()
# User must change on next login
```

### Role Updates
```python
# Change user role
user.set_role('manager')
# Automatically handles admin status
```

## Configuration Parameters

### Password Settings
- Temporary password length: 12 characters
- Expiry time: 24 hours (configurable)
- Minimum password length: 8 characters

### Security Settings
- Session timeout: 1 hour
- Max login attempts: 5
- Password hash algorithm: SHA256

## Common Error Codes

| Error Code | Description                  | Resolution                    |
|------------|------------------------------|-------------------------------|
| 401        | Unauthorized access          | Check login credentials      |
| 403        | Insufficient permissions     | Verify user role            |
| 404        | User not found              | Verify user ID              |
| 409        | Email already exists        | Use different email         |
| 500        | Database operation failed   | Check logs for details      | 

## PDF Generation

### PDF Generation Methods
```python
# Generate PDF from violation
pdf_data = generate_pdf(html_content)

# Handle PDF generation with fallbacks
try:
    pdf_data = generate_pdf(html_content)
    # Return PDF data
except PDFGenerationError:
    # Handle PDF generation failure
```

### PDF Generation Options
| Method | Implementation | Fallback Order |
|--------|---------------|----------------|
| Direct | Memory buffer | Primary method |
| Temp File | File system | First fallback |
| wkhtmltopdf | External tool | Second fallback |

## Violations List

### Pagination Parameters
```python
# API pagination parameters
page = request.args.get('page', 1, type=int)
per_page = request.args.get('per_page', 10, type=int)

# Calculate offset
offset = (page - 1) * per_page
```

### Date Filtering Options
| Filter | Value | Description |
|--------|-------|-------------|
| All Time | 'all' | No date filtering |
| Last 7 Days | '7days' | Violations from past week |
| Last 30 Days | '30days' | Violations from past month |

### Example API Request
```
GET /api/violations?page=1&per_page=10&date_filter=7days
```

### Response Format
```json
{
    "violations": [...],
    "total": 45,
    "page": 1,
    "per_page": 10,
    "pages": 5
}
``` 

## Loading Components

### Spinner Component
```jsx
// Basic spinner usage
<Spinner />

// Size options
<Spinner size="sm" />  // Small
<Spinner size="md" />  // Medium (default)
<Spinner size="lg" />  // Large
<Spinner size="xl" />  // Extra large

// Color options
<Spinner color="blue" />   // Blue (default)
<Spinner color="gray" />   // Gray
<Spinner color="white" />  // White (for dark backgrounds)

// With additional classes
<Spinner className="mt-4" />
```

### LoadingOverlay Component
```jsx
// Basic usage - controlled by isLoading prop
<LoadingOverlay isLoading={isSubmitting} />

// Custom loading message
<LoadingOverlay 
  isLoading={isSubmitting} 
  message="Saving changes..." 
/>

// Custom background opacity (0-100)
<LoadingOverlay 
  isLoading={isSubmitting} 
  opacity={50} 
/>

// Context-sensitive message
<LoadingOverlay 
  isLoading={isSubmitting} 
  message={isUploadingFiles ? "Uploading files..." : "Processing..."} 
/>
```

### Spinner in Forms
```jsx
// Basic spinner in form submit button
<button type="submit" disabled={isSubmitting}>
  {isSubmitting ? <Spinner size="sm" className="mr-2" /> : null}
  Submit
</button>

// Spinner with context-sensitive text
<button type="submit" disabled={isSubmitting}>
  {isSubmitting ? (
    <>
      <Spinner size="sm" className="mr-2" />
      Saving...
    </>
  ) : "Save Changes"}
</button>
```

### Common Loading States
| Component | Loading State | Description |
|-----------|--------------|-------------|
| Form Loading | `const [loading, setLoading] = useState(true)` | Initial data fetch |
| Form Submission | `const [isSubmitting, setIsSubmitting] = useState(false)` | Form submission |
| File Upload | `window.isUploadingFiles = true` | File upload tracking |
| Data Table | `const [isLoading, setIsLoading] = useState(false)` | Data fetching | 

## Unit Profiles

### Database

```sql
CREATE TABLE unit_profiles (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    unit_number VARCHAR(50) NOT NULL, 
    strata_lot_number VARCHAR(50), 
    owner_first_name VARCHAR(100) NOT NULL, 
    owner_last_name VARCHAR(100) NOT NULL, 
    owner_email VARCHAR(255) NOT NULL, 
    owner_telephone VARCHAR(50) NOT NULL, 
    owner_mailing_address TEXT, 
    parking_stall_numbers VARCHAR(255), 
    bike_storage_numbers VARCHAR(255), 
    has_dog BOOL, 
    has_cat BOOL, 
    is_rented BOOL, 
    tenant_first_name VARCHAR(100), 
    tenant_last_name VARCHAR(100), 
    tenant_email VARCHAR(255), 
    tenant_telephone VARCHAR(50), 
    created_at DATETIME, 
    updated_at DATETIME, 
    updated_by INTEGER, 
    PRIMARY KEY (id), 
    FOREIGN KEY(updated_by) REFERENCES users (id) ON DELETE SET NULL, 
    UNIQUE (unit_number)
)
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/units` | GET | List all unit profiles |
| `/api/units` | POST | Create new unit profile |
| `/api/units/<unit_number>` | GET | Get specific unit profile |
| `/api/units/<unit_number>` | PUT | Update unit profile |
| `/api/units/<unit_number>` | DELETE | Delete unit profile |

### Required Packages

- PyMySQL: `pip install PyMySQL` (for MariaDB connectivity) 