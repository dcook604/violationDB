from . import db
from flask_login import UserMixin
from datetime import datetime
import secrets

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(50), default='user')  # Possible values: 'user', 'manager', 'admin'
    temp_password = db.Column(db.String(128))
    temp_password_expiry = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def promote_to_admin(self):
        self.is_admin = True
        self.is_active = True
        self.role = 'admin'
        db.session.commit()

    def activate(self, is_admin=False):
        self.is_active = True
        self.is_admin = is_admin
        if is_admin:
            self.role = 'admin'
        db.session.commit()

    def set_role(self, role):
        valid_roles = ['user', 'manager', 'admin']
        if role not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")
        self.role = role
        if role == 'admin':
            self.is_admin = True
        db.session.commit()

    def set_temporary_password(self, expiry_hours=24):
        """Set a temporary password that expires after the specified hours"""
        temp_pass = secrets.token_urlsafe(12)  # Generate a secure random password
        from werkzeug.security import generate_password_hash
        self.temp_password = generate_password_hash(temp_pass)
        self.temp_password_expiry = datetime.utcnow() + datetime.timedelta(hours=expiry_hours)
        db.session.commit()
        return temp_pass  # Return the plain text temporary password

    def check_temporary_password(self, password):
        """Check if the provided password matches the temporary password and hasn't expired"""
        if not self.temp_password or not self.temp_password_expiry:
            return False
        if datetime.utcnow() > self.temp_password_expiry:
            return False
        from werkzeug.security import check_password_hash
        return check_password_hash(self.temp_password, password)

    def clear_temporary_password(self):
        """Clear the temporary password"""
        self.temp_password = None
        self.temp_password_expiry = None
        db.session.commit()

    def update_last_login(self):
        """Update the last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()

class Violation(db.Model):
    __tablename__ = 'violations'
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
    status = db.Column(db.String(20), default='unresolved')
