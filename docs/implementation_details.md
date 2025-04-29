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