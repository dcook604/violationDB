# User Management Implementation Details

## Database Schema

### User Model
```python
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(50), default='user')
    temp_password = db.Column(db.String(128))
    temp_password_expiry = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
```

## Key Components

### Password Management
- Uses `werkzeug.security` for password hashing
- Temporary passwords use `secrets.token_urlsafe(12)` for secure generation
- Password expiry tracked via `temp_password_expiry` field

### Role System
- Roles: 'user', 'manager', 'admin'
- Admin role automatically sets `is_admin=True`
- Role changes handled through `set_role()` method

### Security Features
- Password hashing for both regular and temporary passwords
- Automatic temporary password expiration
- Session management with Flask-Login
- Role-based access control

## API Methods

### User Creation
```python
@classmethod
def generate_temp_password(cls)  # Generates secure temporary password
def set_temporary_password(self, expiry_hours=24)  # Sets up temporary access
```

### User Management
```python
def promote_to_admin(self)  # Promotes user to admin role
def activate(self, is_admin=False)  # Activates user account
def set_role(self, role)  # Updates user role with validation
```

### Password Handling
```python
def check_temporary_password(self, password)  # Validates temporary password
def clear_temporary_password(self)  # Removes temporary access
def update_last_login(self)  # Updates login timestamp
```

## Routes and Endpoints

### User Management Routes
- `/admin/users` - List all users
- `/admin/users/create` - Create new user
- `/admin/users/<id>/edit` - Edit user details
- `/admin/users/<id>/delete` - Delete user
- `/admin/users/<id>/change-password` - Change user password

## Forms

### User Creation Form
- Email validation
- Role selection
- Active status toggle

### User Edit Form
- Email update
- Role modification
- Temporary password reset option

### Password Change Form
- New password input
- Password confirmation
- Minimum length validation 

# PDF Generation Implementation

## PDF Generation Methods

### PDF Generation with WeasyPrint
- Uses WeasyPrint 61.2 with fallback mechanisms
- Direct rendering with memory buffer as primary method
- Temporary file approach as first fallback
- wkhtmltopdf as secondary fallback option

### Compatibility Considerations
- WeasyPrint 61.2 has known compatibility issues with pydyf library
- Comprehensive error handling and logging for all PDF generation attempts
- Multiple redundancy methods ensure PDF availability

## Key Components

### PDF Generation Process
```python
def generate_pdf(html_content):
    # Primary approach: Direct rendering to memory buffer
    try:
        buffer = BytesIO()
        HTML(string=html_content).write_pdf(buffer)
        buffer.seek(0)
        return buffer
    except Exception as e:
        logger.error(f"Direct PDF generation failed: {e}")
        
        # First fallback: Using temporary files
        try:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
                HTML(string=html_content).write_pdf(temp_pdf.name)
                return open(temp_pdf.name, 'rb')
        except Exception as e:
            logger.error(f"Temporary file PDF generation failed: {e}")
            
            # Second fallback: wkhtmltopdf
            try:
                buffer = BytesIO()
                pdfkit.from_string(html_content, buffer)
                buffer.seek(0)
                return buffer
            except Exception as e:
                logger.error(f"wkhtmltopdf generation failed: {e}")
                raise PDFGenerationError("All PDF generation methods failed")
```

# Violations List Implementation

## Pagination System

### Pagination Implementation
- Frontend pagination with server-side data fetching
- Page size options: 5, 10, 25, 50 items per page
- API supports offset/limit parameters for efficient data retrieval

### Date Filtering
- Quick filter options: Last 7 Days, Last 30 Days, All Time
- Filter parameters passed to API endpoint
- Maintains loading state during filter changes

## API Endpoints

### Violations Listing Endpoint
```python
@app.route('/api/violations', methods=['GET'])
def get_violations():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    date_filter = request.args.get('date_filter', 'all')
    
    # Date filter logic
    query = Violation.query
    if date_filter == '7days':
        query = query.filter(Violation.created_at >= datetime.utcnow() - timedelta(days=7))
    elif date_filter == '30days':
        query = query.filter(Violation.created_at >= datetime.utcnow() - timedelta(days=30))
    
    # Pagination
    offset = (page - 1) * per_page
    violations = query.order_by(Violation.created_at.desc()).offset(offset).limit(per_page).all()
    total = query.count()
    
    return jsonify({
        'violations': [v.to_dict() for v in violations],
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    })
```

# Dashboard Enhancements

## Recent Violations Table

### Category Display
- Fixed category name display in dashboard recent violations table
- Updated API to provide category information in violation list
- Maintains backward compatibility with existing dashboard functionality

### Document Links
- Improved styling for HTML/PDF document links
- Better visibility with distinct button designs
- Updated API to ensure document links are always available 