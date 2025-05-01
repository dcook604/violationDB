from . import db
from flask_login import UserMixin
from datetime import datetime, timedelta
import secrets
from werkzeug.security import generate_password_hash, check_password_hash

class UserError(Exception):
    """Base exception for user-related errors"""
    pass

class InvalidRoleError(UserError):
    """Raised when an invalid role is assigned"""
    pass

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    # Role constants
    ROLE_USER = 'user'
    ROLE_MANAGER = 'manager'
    ROLE_ADMIN = 'admin'
    VALID_ROLES = [ROLE_USER, ROLE_MANAGER, ROLE_ADMIN]
    
    # Database columns
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(50), default=ROLE_USER)
    temp_password = db.Column(db.String(128))
    temp_password_expiry = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    @classmethod
    def generate_temp_password(cls, length=12):
        """Generate a secure temporary password
        
        Args:
            length (int): Length of the temporary password
            
        Returns:
            str: Secure temporary password
        """
        return secrets.token_urlsafe(length)

    def promote_to_admin(self):
        """Promote user to admin role with full privileges"""
        self.is_admin = True
        self.is_active = True
        self.role = self.ROLE_ADMIN
        db.session.commit()

    def activate(self, is_admin=False):
        """Activate user account
        
        Args:
            is_admin (bool): Whether to also grant admin privileges
        """
        self.is_active = True
        if is_admin:
            self.is_admin = True
            self.role = self.ROLE_ADMIN
        db.session.commit()

    def set_role(self, role):
        """Set user role with validation
        
        Args:
            role (str): New role to assign
            
        Raises:
            InvalidRoleError: If role is not valid
        """
        if role not in self.VALID_ROLES:
            raise InvalidRoleError(f"Invalid role. Must be one of: {', '.join(self.VALID_ROLES)}")
        
        self.role = role
        if role == self.ROLE_ADMIN:
            self.is_admin = True
            self.is_active = True
        db.session.commit()

    def set_temporary_password(self, expiry_hours=24):
        """Set a temporary password that expires after specified hours
        
        Args:
            expiry_hours (int): Hours until password expires
            
        Returns:
            str: Plain text temporary password
        """
        temp_pass = self.generate_temp_password()
        self.temp_password = generate_password_hash(temp_pass)
        self.temp_password_expiry = datetime.utcnow() + timedelta(hours=expiry_hours)
        db.session.commit()
        return temp_pass

    def check_temporary_password(self, password):
        """Check if temporary password is valid and not expired
        
        Args:
            password (str): Password to check
            
        Returns:
            bool: True if password is valid and not expired
        """
        if not self.temp_password or not self.temp_password_expiry:
            return False
        if datetime.utcnow() > self.temp_password_expiry:
            return False
        return check_password_hash(self.temp_password, password)

    def clear_temporary_password(self):
        """Clear temporary password and expiry"""
        self.temp_password = None
        self.temp_password_expiry = None
        db.session.commit()

    def update_last_login(self):
        """Update last login timestamp to current UTC time"""
        self.last_login = datetime.utcnow()
        db.session.commit()

    def set_password(self, password):
        """Set user's password hash
        
        Args:
            password (str): Plain text password to hash and store
        """
        self.password_hash = generate_password_hash(password)
        db.session.commit()

    def check_password(self, password):
        """Check if password matches stored hash
        
        Args:
            password (str): Password to check
            
        Returns:
            bool: True if password matches
        """
        return check_password_hash(self.password_hash, password)

class Violation(db.Model):
    __tablename__ = 'violations'
    
    # Status constants
    STATUS_ACTIVE = 'active'
    STATUS_RESOLVED = 'resolved'
    STATUS_PENDING = 'pending'
    VALID_STATUSES = [STATUS_ACTIVE, STATUS_RESOLVED, STATUS_PENDING]
    
    reference = db.Column(db.String(32), unique=True, nullable=False, index=True)
    extra_fields = db.Column(db.JSON, default=dict)
    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    resident_name = db.Column(db.String(120))
    resident_email = db.Column(db.String(120))
    unit_number = db.Column(db.String(20))
    incident_date = db.Column(db.Date)
    incident_time = db.Column(db.Time)
    incident_place = db.Column(db.String(120))
    infraction_details = db.Column(db.Text)
    bylaw_sections_violated = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(50))
    building = db.Column(db.String(100))
    incident_area = db.Column(db.String(100))
    report_to = db.Column(db.String(100))
    concierge_shift = db.Column(db.String(50))
    people_involved = db.Column(db.Text)
    noticed_by = db.Column(db.String(100))
    people_called = db.Column(db.Text)
    subject = db.Column(db.String(255))
    details = db.Column(db.Text)
    initial_action = db.Column(db.Text)
    resolution = db.Column(db.Text)
    photo_paths = db.Column(db.Text)  # comma-separated
    pdf_paths = db.Column(db.Text)    # comma-separated
    pdf_letter_path = db.Column(db.String(255))
    html_path = db.Column(db.String(255))  # Path to the generated HTML file
    pdf_path = db.Column(db.String(255))   # Path to the generated PDF file
    status = db.Column(db.String(20), default=STATUS_ACTIVE)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.status:
            self.status = self.STATUS_ACTIVE

    def resolve(self, user_id):
        """Mark violation as resolved
        
        Args:
            user_id (int): ID of user resolving the violation
        """
        self.status = self.STATUS_RESOLVED
        self.resolved_at = datetime.utcnow()
        self.resolved_by = user_id
        db.session.commit()

    def reopen(self):
        """Reopen a resolved violation"""
        self.status = self.STATUS_ACTIVE
        self.resolved_at = None
        self.resolved_by = None
        db.session.commit()

    @property
    def is_resolved(self):
        """Check if violation is resolved
        
        Returns:
            bool: True if resolved
        """
        return self.status == self.STATUS_RESOLVED

class FieldDefinition(db.Model):
    __tablename__ = 'field_definitions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)  # Internal name
    label = db.Column(db.String(128), nullable=False)  # Display label
    type = db.Column(db.String(32), nullable=False)  # text, number, date, select, etc.
    required = db.Column(db.Boolean, default=False)
    options = db.Column(db.Text)  # JSON-encoded list for select fields
    order = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean, default=True)
    validation = db.Column(db.Text)  # JSON-encoded validation rules (optional)
    grid_column = db.Column(db.Integer, default=0)  # 0 = full width, 1-12 = grid columns for layout
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<FieldDefinition {self.name} ({self.type})>'

class ViolationFieldValue(db.Model):
    __tablename__ = 'violation_field_values'
    id = db.Column(db.Integer, primary_key=True)
    violation_id = db.Column(db.Integer, db.ForeignKey('violations.id'), nullable=False)
    field_definition_id = db.Column(db.Integer, db.ForeignKey('field_definitions.id'), nullable=False)
    value = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    field_definition = db.relationship('FieldDefinition')

    def __repr__(self):
        return f'<ViolationFieldValue V:{self.violation_id} F:{self.field_definition_id}>'

class Settings(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    
    # SMTP Settings
    smtp_server = db.Column(db.String(255))
    smtp_port = db.Column(db.Integer)
    smtp_username = db.Column(db.String(255))
    smtp_password = db.Column(db.String(255))
    smtp_use_tls = db.Column(db.Boolean, default=True)
    smtp_from_email = db.Column(db.String(255))
    smtp_from_name = db.Column(db.String(255))
    
    # Global Notification Settings
    notification_emails = db.Column(db.Text)  # Comma-separated list of emails
    enable_global_notifications = db.Column(db.Boolean, default=False)
    
    # Additional settings
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get the active settings or create default settings if none exist"""
        settings = cls.query.first()
        if not settings:
            settings = cls()
            db.session.add(settings)
            db.session.commit()
        return settings
    
    def get_notification_emails_list(self):
        """Convert notification_emails string to a list of email addresses"""
        if not self.notification_emails:
            return []
        return [email.strip() for email in self.notification_emails.split(',') if email.strip()]
        
    def __repr__(self):
        return f'<Settings id={self.id}>'

class ViolationReply(db.Model):
    __tablename__ = 'violation_replies'
    
    id = db.Column(db.Integer, primary_key=True)
    violation_id = db.Column(db.Integer, db.ForeignKey('violations.id'), nullable=False)
    email = db.Column(db.String(255), nullable=False)  # Email of the person replying
    response_text = db.Column(db.Text, nullable=False)  # The reply content
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(50))  # IP address of the responder for audit
    
    # Relationships
    violation = db.relationship('Violation', backref=db.backref('replies', lazy='dynamic'))
    
    def __repr__(self):
        return f'<ViolationReply id={self.id} for violation_id={self.violation_id}>'
