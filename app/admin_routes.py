from flask import Blueprint, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from .models import User, FieldDefinition, Settings
from . import db
from werkzeug.security import generate_password_hash
import json
from .utils import clear_field_cache

admin_bp = Blueprint('admin', __name__)

# Decorator to restrict access to admin users
def admin_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            return jsonify({"error": "Admin privileges required"}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Removed old user management routes as they are now handled in user_routes.py

@admin_bp.route('/api/fields', methods=['GET'])
@admin_required
def list_fields():
    fields = FieldDefinition.query.order_by(FieldDefinition.order).all()
    return jsonify([{
        'id': f.id,
        'name': f.name,
        'label': f.label,
        'type': f.type,
        'required': f.required,
        'options': f.options,
        'order': f.order,
        'active': f.active,
        'validation': f.validation
    } for f in fields])

@admin_bp.route('/api/fields', methods=['POST'])
@admin_required
def create_field():
    data = request.get_json()
    field = FieldDefinition(
        name=data['name'],
        label=data.get('label', data['name']),
        type=data['type'],
        required=data.get('required', False),
        options=data.get('options'),
        order=data.get('order', 0),
        active=data.get('active', True),
        validation=data.get('validation')
    )
    db.session.add(field)
    db.session.commit()
    
    # Clear field cache after creating a new field
    clear_field_cache()
    
    return jsonify({'message': 'Field created', 'id': field.id}), 201

@admin_bp.route('/api/fields/<int:fid>', methods=['PUT'])
@admin_required
def update_field(fid):
    field = FieldDefinition.query.get_or_404(fid)
    data = request.get_json()
    field.label = data.get('label', field.label)
    field.type = data.get('type', field.type)
    field.required = data.get('required', field.required)
    field.options = data.get('options', field.options)
    field.order = data.get('order', field.order)
    field.active = data.get('active', field.active)
    field.validation = data.get('validation', field.validation)
    db.session.commit()
    
    # Clear field cache after updating a field
    clear_field_cache()
    
    return jsonify({'message': 'Field updated'})

@admin_bp.route('/api/fields/<int:fid>', methods=['DELETE'])
@admin_required
def delete_field(fid):
    field = FieldDefinition.query.get_or_404(fid)
    db.session.delete(field)
    db.session.commit()
    
    # Clear field cache after deleting a field
    clear_field_cache()
    
    return jsonify({'message': 'Field deleted'})

@admin_bp.route('/api/fields/<int:fid>/toggle', methods=['POST'])
@admin_required
def toggle_field(fid):
    field = FieldDefinition.query.get_or_404(fid)
    field.active = not field.active
    db.session.commit()
    
    # Clear field cache after toggling a field
    clear_field_cache()
    
    return jsonify({'message': 'Field toggled', 'active': field.active})

@admin_bp.route('/api/fields/reorder', methods=['POST'])
@admin_required
def reorder_fields():
    data = request.get_json()
    for idx, fid in enumerate(data['order']):
        field = FieldDefinition.query.get(fid)
        if field:
            field.order = idx
    db.session.commit()
    
    # Clear field cache after reordering fields
    clear_field_cache()
    
    return jsonify({'message': 'Fields reordered'})

@admin_bp.route('/api/admin/settings', methods=['GET'])
@admin_required
def get_settings():
    """Get the current settings"""
    settings = Settings.get_settings()
    
    # Don't include the password in the response
    return jsonify({
        'id': settings.id,
        'smtp_server': settings.smtp_server or '',
        'smtp_port': settings.smtp_port or 25,
        'smtp_username': settings.smtp_username or '',
        'smtp_use_tls': settings.smtp_use_tls or True,
        'smtp_from_email': settings.smtp_from_email or '',
        'smtp_from_name': settings.smtp_from_name or '',
        'notification_emails': settings.notification_emails or '',
        'enable_global_notifications': settings.enable_global_notifications or False,
        'updated_at': settings.updated_at.isoformat() if settings.updated_at else None
    })

@admin_bp.route('/api/admin/settings', methods=['PUT'])
@admin_required
def update_settings():
    """Update settings"""
    settings = Settings.get_settings()
    data = request.json or {}
    
    # Update SMTP settings
    if 'smtp_server' in data:
        settings.smtp_server = data['smtp_server']
    if 'smtp_port' in data:
        settings.smtp_port = data['smtp_port']
    if 'smtp_username' in data:
        settings.smtp_username = data['smtp_username']
    if 'smtp_password' in data and data['smtp_password']:
        # Only update password if a new one is provided
        settings.smtp_password = data['smtp_password']
    if 'smtp_use_tls' in data:
        settings.smtp_use_tls = data['smtp_use_tls']
    if 'smtp_from_email' in data:
        settings.smtp_from_email = data['smtp_from_email']
    if 'smtp_from_name' in data:
        settings.smtp_from_name = data['smtp_from_name']
    
    # Update notification settings
    if 'notification_emails' in data:
        settings.notification_emails = data['notification_emails']
    if 'enable_global_notifications' in data:
        settings.enable_global_notifications = data['enable_global_notifications']
    
    # Record who updated the settings
    settings.updated_by = current_user.id
    
    db.session.commit()
    
    return jsonify({
        'message': 'Settings updated successfully',
        'updated_at': settings.updated_at.isoformat() if settings.updated_at else None
    })

@admin_bp.route('/api/admin/settings/test-email', methods=['POST'])
@admin_required
def test_email():
    """Send a test email using the current settings"""
    from .utils import send_email
    
    data = request.json or {}
    recipient = data.get('email') or current_user.email
    
    if not recipient:
        return jsonify({'error': 'No recipient email provided'}), 400
    
    try:
        send_email(
            subject="Test Email from Violation System",
            recipients=[recipient],
            body="This is a test email from the Violation System to verify that email sending is properly configured.",
            html="<p>This is a test email from the Violation System to verify that email sending is properly configured.</p>"
        )
        return jsonify({'message': f'Test email sent to {recipient}'})
    except Exception as e:
        current_app.logger.error(f"Error sending test email: {str(e)}")
        return jsonify({'error': f'Failed to send test email: {str(e)}'}), 500
