from . import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Violation(db.Model):
    __tablename__ = 'violations'
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
