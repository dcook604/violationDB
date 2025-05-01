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

# Security Enhancements

## Password Security

### Argon2id Password Hashing
- Uses Argon2id, the winner of the Password Hashing Competition
- Configured with time_cost=3, memory_cost=65536 (64MB), parallelism=4
- Automatically migrates passwords from Werkzeug's default hashing
- Includes automatic hash rehashing when parameters change

### Account Lockout
```python
class User(UserMixin, db.Model):
    # Max failed login attempts before lockout
    MAX_FAILED_ATTEMPTS = 10
    
    # Account lockout fields
    failed_login_attempts = db.Column(db.Integer, default=0)
    last_failed_login = db.Column(db.DateTime)
    account_locked_until = db.Column(db.DateTime)
    password_algorithm = db.Column(db.String(20), default='argon2')
```

## Login Security

### Failed Login Handling
- Tracks failed login attempts per user
- Provides warnings when approaching the lockout threshold
- Temporarily locks accounts after 10 failed attempts
- 30-minute automatic lockout period

### Account Unlocking
```python
@auth.route('/api/auth/unlock-account', methods=['POST', 'OPTIONS'])
@cors_preflight
@login_required
def unlock_account():
    """Admin endpoint to unlock a locked user account"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin permissions required'}), 403
    
    # ... implementation details ...
```

## Security Migration

### Database Migration
- Updated password_hash field length to accommodate Argon2id hashes
- Added fields for tracking login attempts and account locks
- Migration includes both Alembic and direct SQL scripts
- Graceful handling of existing password hashes

### Password Migration
- Seamless migration during user login
- No user disruption during transition
- Multiple hash verification strategies for compatibility 

# Session Management Implementation

## Session Security

### Session Timeouts
```python
# Session timeout settings in app/config.py
PERMANENT_SESSION_LIFETIME = timedelta(hours=24)  # Absolute timeout
IDLE_TIMEOUT_MINUTES = 30  # Idle timeout in minutes
```

### User Session Model
```python
class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    user_agent = db.Column(db.String(255))
    ip_address = db.Column(db.String(45))
```

## Session Workflows

### Session Creation
- Token-based session management with secure UUIDs
- Flask-Login handles authentication 
- Additional UserSession tracks session details
- Session tokens stored as HttpOnly cookies

### Session Validation
- Absolute timeout of 24 hours from creation
- Idle timeout of 30 minutes since last activity
- Activity auto-refreshed on any authenticated request
- Expired sessions are automatically terminated

### Multi-Session Control
- Option to enforce single session per user
- Upon login, all other sessions are terminated
- Users can view and manage their active sessions
- Admin users can terminate any user's sessions

## API Endpoints

### Session Management Routes
- `/api/auth/active-sessions` - List all active sessions for current user
- `/api/auth/terminate-sessions` - Terminate all other sessions
- `/api/auth/terminate-session/<id>` - Terminate a specific session
- `/api/auth/session` - Validate current session status

### Session Token Security
- Session tokens are 128-bit UUIDs stored as HttpOnly cookies
- Tokens are validated against stored sessions on every request
- Tokens are invalidated upon logout
- Cookies cleared on both client and server during logout 