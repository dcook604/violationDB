from . import db
from flask_login import UserMixin
from datetime import datetime, timedelta
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
import argon2
import uuid
from sqlalchemy.dialects.mysql import JSON # If using MySQL for JSON storage
from sqlalchemy.ext.mutable import MutableDict # For JSON mutation tracking

# Create Argon2 password hasher
ph = argon2.PasswordHasher(
    time_cost=3,       # Number of iterations
    memory_cost=65536, # Memory usage in kibibytes (64MB)
    parallelism=4,     # Number of parallel threads
    hash_len=32,       # Length of the hash in bytes
    salt_len=16        # Length of the random salt in bytes
)

class UserError(Exception):
    """Base exception for user-related errors"""
    pass

class InvalidRoleError(UserError):
    """Raised when an invalid role is assigned"""
    pass

class AccountLockedError(UserError):
    """Raised when login is attempted on a locked account"""
    pass

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    # Role constants
    ROLE_USER = 'user'
    ROLE_MANAGER = 'manager'
    ROLE_ADMIN = 'admin'
    VALID_ROLES = [ROLE_USER, ROLE_MANAGER, ROLE_ADMIN]
    
    # Max failed login attempts before lockout
    MAX_FAILED_ATTEMPTS = 10
    
    # Database columns
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)  # Increased length for Argon2
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(50), default=ROLE_USER)
    temp_password = db.Column(db.String(255))  # Increased length for Argon2
    temp_password_expiry = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # New columns for account lockout
    failed_login_attempts = db.Column(db.Integer, default=0)
    last_failed_login = db.Column(db.DateTime)
    account_locked_until = db.Column(db.DateTime)
    password_algorithm = db.Column(db.String(20), default='argon2')  # Track password hash algorithm
    position = db.Column(db.String(50), nullable=True)  # Council, Property Manager, Caretaker, Cleaner, Concierge

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
        if self.password_algorithm == 'argon2':
            self.temp_password = ph.hash(temp_pass)
        else:
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
            
        # Check if account is locked
        if self.is_account_locked():
            return False
            
        try:
            if self.password_algorithm == 'argon2' and self.temp_password.startswith('$argon2'):
                return ph.verify(self.temp_password, password)
            else:
                return check_password_hash(self.temp_password, password)
        except Exception:
            return False

    def clear_temporary_password(self):
        """Clear temporary password and expiry"""
        self.temp_password = None
        self.temp_password_expiry = None
        db.session.commit()

    def update_last_login(self):
        """Update last login timestamp to current UTC time and reset failed attempts"""
        self.last_login = datetime.utcnow()
        self.failed_login_attempts = 0
        self.account_locked_until = None
        db.session.commit()

    def set_password(self, password):
        """Set user's password hash
        
        Args:
            password (str): Plain text password to hash and store
        """
        if self.password_algorithm == 'argon2':
            self.password_hash = ph.hash(password)
        else:
            self.password_hash = generate_password_hash(password)
        db.session.commit()
        
    def migrate_to_argon2(self, password):
        """Migrate user's password to Argon2id hash
        
        Args:
            password (str): Plain text password to rehash
        """
        self.password_hash = ph.hash(password)
        self.password_algorithm = 'argon2'
        db.session.commit()

    def check_password(self, password):
        """Check if password matches stored hash
        
        Args:
            password (str): Password to check
            
        Returns:
            bool: True if password matches
        """
        # Check if account is locked
        if self.is_account_locked():
            raise AccountLockedError(f"Account locked until {self.account_locked_until}")
            
        try:
            # If using Argon2id
            if self.password_algorithm == 'argon2' and self.password_hash.startswith('$argon2'):
                is_valid = ph.verify(self.password_hash, password)
                
                # Check if hash needs rehashing (parameters changed, etc)
                if ph.check_needs_rehash(self.password_hash):
                    self.password_hash = ph.hash(password)
                    db.session.commit()
                
                return is_valid
            else:
                # Using Werkzeug's check_password_hash for older hashes
                return check_password_hash(self.password_hash, password)
                
        except argon2.exceptions.VerifyMismatchError:
            self.record_failed_login()
            return False
        except Exception:
            self.record_failed_login()
            return False
            
    def record_failed_login(self):
        """Record a failed login attempt and lock account if needed"""
        self.failed_login_attempts += 1
        self.last_failed_login = datetime.utcnow()
        
        # Lock account if max attempts reached
        if self.failed_login_attempts >= self.MAX_FAILED_ATTEMPTS:
            # Lock for 30 minutes
            self.account_locked_until = datetime.utcnow() + timedelta(minutes=30)
            
        db.session.commit()
        
    def is_account_locked(self):
        """Check if account is currently locked
        
        Returns:
            bool: True if account is locked
        """
        if not self.account_locked_until:
            return False
            
        # If lock time has passed, unlock the account
        if datetime.utcnow() > self.account_locked_until:
            self.account_locked_until = None
            db.session.commit()
            return False
            
        return True
        
    def unlock_account(self):
        """Manually unlock a locked account"""
        self.failed_login_attempts = 0
        self.account_locked_until = None
        db.session.commit()

    # Session management methods
    def create_session(self, user_agent=None, ip_address=None):
        """Create a new session for the user
        
        Args:
            user_agent (str): Browser/client user agent
            ip_address (str): Client IP address
            
        Returns:
            UserSession: The created session
        """
        # First cleanup expired sessions
        self.cleanup_expired_sessions()
        
        # Create new session
        session = UserSession(
            user_id=self.id,
            token=str(uuid.uuid4()),
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=datetime.utcnow() + timedelta(hours=24)  # 24-hour absolute timeout
        )
        db.session.add(session)
        db.session.commit()
        return session
    
    def get_active_sessions(self):
        """Get all active sessions for this user
        
        Returns:
            list: List of active UserSession objects
        """
        return UserSession.query.filter_by(
            user_id=self.id, 
            is_active=True
        ).order_by(UserSession.last_activity.desc()).all()
    
    def terminate_other_sessions(self, current_session_id):
        """Terminate all sessions except the current one
        
        Args:
            current_session_id (int): ID of the current session to keep
            
        Returns:
            int: Number of sessions terminated
        """
        sessions = UserSession.query.filter(
            UserSession.user_id == self.id,
            UserSession.id != current_session_id,
            UserSession.is_active == True
        ).all()
        
        count = 0
        for session in sessions:
            session.terminate()
            count += 1
        
        db.session.commit()
        return count
    
    def terminate_all_sessions(self):
        """Terminate all active sessions for this user
        
        Returns:
            int: Number of sessions terminated
        """
        sessions = UserSession.query.filter_by(
            user_id=self.id,
            is_active=True
        ).all()
        
        count = 0
        for session in sessions:
            session.terminate()
            count += 1
        
        db.session.commit()
        return count
        
    def cleanup_expired_sessions(self):
        """Clean up expired sessions for this user"""
        now = datetime.utcnow()
        
        # Find expired sessions
        expired_sessions = UserSession.query.filter(
            UserSession.user_id == self.id,
            UserSession.is_active == True,
            UserSession.expires_at < now
        ).all()
        
        # Mark them as inactive
        for session in expired_sessions:
            session.terminate()
            
        db.session.commit()

class Violation(db.Model):
    __tablename__ = 'violations'
    
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), nullable=True)
    reference = db.Column(db.String(50), unique=True)
    category = db.Column(db.String(255))
    building = db.Column(db.String(255))
    unit_number = db.Column(db.String(50))
    incident_date = db.Column(db.Date)
    incident_time = db.Column(db.String(20))
    subject = db.Column(db.String(255))
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    html_path = db.Column(db.String(255))
    pdf_path = db.Column(db.String(255))
    status = db.Column(db.String(64), default='Open', nullable=False)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    # --- Static Violation Fields (2024) ---
    owner_property_manager_first_name = db.Column(db.String(100))
    owner_property_manager_last_name = db.Column(db.String(100))
    owner_property_manager_email = db.Column(db.String(255))
    owner_property_manager_telephone = db.Column(db.String(50))
    where_did = db.Column(db.String(100))
    was_security_or_police_called = db.Column(db.String(100))
    fine_levied = db.Column(db.String(100))
    action_taken = db.Column(db.Text)
    tenant_first_name = db.Column(db.String(100))
    tenant_last_name = db.Column(db.String(100))
    tenant_email = db.Column(db.String(255))
    tenant_phone = db.Column(db.String(50))
    concierge_shift = db.Column(db.String(100))
    noticed_by = db.Column(db.String(100))
    people_called = db.Column(db.String(255))
    actioned_by = db.Column(db.String(100))
    people_involved = db.Column(db.String(255))
    incident_details = db.Column(db.Text)
    attach_evidence = db.Column(db.Text)  # JSON-encoded list or metadata

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.status:
            self.status = 'Open'

    def resolve(self, user_id):
        """Mark violation as resolved
        
        Args:
            user_id (int): ID of user resolving the violation
        """
        self.status = 'Resolved'
        self.resolved_at = datetime.utcnow()
        self.resolved_by = user_id
        db.session.commit()

    def reopen(self):
        """Reopen a resolved violation"""
        self.status = 'Open'
        self.resolved_at = None
        self.resolved_by = None
        db.session.commit()

    @property
    def is_resolved(self):
        """Check if violation is resolved
        
        Returns:
            bool: True if resolved
        """
        return self.status == 'Resolved'

    def to_dict(self):
        return {
            'id': self.id,
            'public_id': self.public_id,
            'reference': self.reference,
            'category': self.category,
            'building': self.building,
            'unit_number': self.unit_number,
            'incident_date': self.incident_date.isoformat() if self.incident_date else None,
            'incident_time': self.incident_time,
            'subject': self.subject,
            'details': self.details,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by,
            'html_path': self.html_path,
            'pdf_path': self.pdf_path,
            'status': self.status,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolved_by': self.resolved_by,
            # --- Static Violation Fields (2024) ---
            'owner_property_manager_first_name': self.owner_property_manager_first_name,
            'owner_property_manager_last_name': self.owner_property_manager_last_name,
            'owner_property_manager_email': self.owner_property_manager_email,
            'owner_property_manager_telephone': self.owner_property_manager_telephone,
            'where_did': self.where_did,
            'was_security_or_police_called': self.was_security_or_police_called,
            'fine_levied': self.fine_levied,
            'action_taken': self.action_taken,
            'tenant_first_name': self.tenant_first_name,
            'tenant_last_name': self.tenant_last_name,
            'tenant_email': self.tenant_email,
            'tenant_phone': self.tenant_phone,
            'concierge_shift': self.concierge_shift,
            'noticed_by': self.noticed_by,
            'people_called': self.people_called,
            'actioned_by': self.actioned_by,
            'people_involved': self.people_involved,
            'incident_details': self.incident_details,
            'attach_evidence': self.attach_evidence,
        }

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

class UserSession(db.Model):
    """Model for tracking user sessions"""
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    user_agent = db.Column(db.String(255))
    ip_address = db.Column(db.String(45))  # IPv6 can be up to 45 chars
    
    # Relationship to User
    user = db.relationship('User', backref=db.backref('sessions', lazy='dynamic'))
    
    def __init__(self, **kwargs):
        super(UserSession, self).__init__(**kwargs)
        if 'expires_at' not in kwargs:
            self.expires_at = datetime.utcnow() + timedelta(hours=24)
    
    def update_activity(self):
        """Update the last activity timestamp and extend session if needed"""
        now = datetime.utcnow()
        self.last_activity = now
        
        # If less than 30 minutes remain, extend by another 30 minutes
        # This implements the sliding window for idle timeout
        if self.expires_at - now < timedelta(minutes=10):
            # Only extend up to the maximum 24 hours from creation
            max_expiry = self.created_at + timedelta(hours=24)
            new_expiry = now + timedelta(minutes=30)
            self.expires_at = min(new_expiry, max_expiry)
            
        db.session.commit()
    
    def is_expired(self):
        """Check if the session has expired
        
        Returns:
            bool: True if expired
        """
        return datetime.utcnow() > self.expires_at
    
    def is_idle_timeout(self):
        """Check if the session has exceeded the idle timeout (30 minutes)
        
        Returns:
            bool: True if idle timeout exceeded
        """
        idle_time = datetime.utcnow() - self.last_activity
        return idle_time > timedelta(minutes=30)
    
    def terminate(self):
        """Terminate this session"""
        self.is_active = False
        db.session.commit()
        
    def __repr__(self):
        return f'<UserSession id={self.id} user_id={self.user_id} active={self.is_active}>'

class ViolationAccess(db.Model):
    __tablename__ = 'violation_access_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    violation_id = db.Column(db.Integer, db.ForeignKey('violations.id'), nullable=False)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(255))
    accessed_at = db.Column(db.DateTime, default=datetime.utcnow)
    token = db.Column(db.String(255))
    
    # Relationship
    violation = db.relationship('Violation', backref=db.backref('access_logs', lazy='dynamic'))

class ViolationStatusLog(db.Model):
    __tablename__ = 'violation_status_log'
    id = db.Column(db.Integer, primary_key=True)
    violation_id = db.Column(db.Integer, db.ForeignKey('violations.id'), nullable=False)
    old_status = db.Column(db.String(64), nullable=False)
    new_status = db.Column(db.String(64), nullable=False)
    changed_by = db.Column(db.String(128), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

class UnitProfile(db.Model):
    __tablename__ = 'unit_profiles'
    id = db.Column(db.Integer, primary_key=True)
    unit_number = db.Column(db.String(50), nullable=False, unique=True)
    strata_lot_number = db.Column(db.String(50), nullable=True)
    # Owner Information
    owner_first_name = db.Column(db.String(100), nullable=False)
    owner_last_name = db.Column(db.String(100), nullable=False)
    owner_email = db.Column(db.String(255), nullable=False)
    owner_telephone = db.Column(db.String(50), nullable=False)
    owner_mailing_address = db.Column(db.Text, nullable=True)
    # Storage Information
    parking_stall_numbers = db.Column(db.String(255), nullable=True) # Store as comma-separated string initially
    bike_storage_numbers = db.Column(db.String(255), nullable=True) # Store as comma-separated string initially
    # Consider using JSON type if DB supports it and needs structure:
    # parking_stall_numbers = db.Column(MutableDict.as_mutable(JSON), nullable=True) 
    # Pet Information
    has_dog = db.Column(db.Boolean, default=False)
    has_cat = db.Column(db.Boolean, default=False)
    # Rental Status & Tenant Info
    is_rented = db.Column(db.Boolean, default=False)
    tenant_first_name = db.Column(db.String(100), nullable=True)
    tenant_last_name = db.Column(db.String(100), nullable=True)
    tenant_email = db.Column(db.String(255), nullable=True)
    tenant_telephone = db.Column(db.String(50), nullable=True)
    # Audit Information
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    # Relationship to updater (optional)
    updater = db.relationship('User', backref='updated_unit_profiles')

    def to_dict(self):
        return {
            'id': self.id,
            'unit_number': self.unit_number,
            'strata_lot_number': self.strata_lot_number,
            'owner_first_name': self.owner_first_name,
            'owner_last_name': self.owner_last_name,
            'owner_email': self.owner_email,
            'owner_telephone': self.owner_telephone,
            'owner_mailing_address': self.owner_mailing_address,
            'parking_stall_numbers': self.parking_stall_numbers,
            'bike_storage_numbers': self.bike_storage_numbers,
            'has_dog': self.has_dog,
            'has_cat': self.has_cat,
            'is_rented': self.is_rented,
            'tenant_first_name': self.tenant_first_name,
            'tenant_last_name': self.tenant_last_name,
            'tenant_email': self.tenant_email,
            'tenant_telephone': self.tenant_telephone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by,
            'updater_email': self.updater.email if self.updater else None
        }

# If implementing the generic audit log:
# class AuditLog(db.Model):
#     __tablename__ = 'audit_log'
#     id = db.Column(db.Integer, primary_key=True)
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
#     action = db.Column(db.String(50), nullable=False)
#     target_table = db.Column(db.String(100), nullable=False)
#     target_id = db.Column(db.Integer, nullable=False)
#     details = db.Column(db.Text, nullable=True) # Store changes as JSON string?
#     # Relationship to user (optional)
#     user = db.relationship('User', backref='audit_logs')
