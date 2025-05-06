from flask import Blueprint, redirect, url_for, flash, request, jsonify, current_app
from flask_jwt_extended import get_jwt, get_jwt_identity
from app.jwt_auth import jwt_required_api
from .models import User, FieldDefinition, Settings
from . import db
from werkzeug.security import generate_password_hash
import json
from .utils import clear_field_cache

admin_bp = Blueprint('admin', __name__)

# Decorator to restrict access to admin users
def admin_required(f):
    def decorated_function(*args, **kwargs):
        claims = get_jwt()
        is_admin = claims.get('is_admin')
        user_id = get_jwt_identity()
        if not is_admin:
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
        'validation': f.validation,
        'grid_column': f.grid_column
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
        validation=data.get('validation'),
        grid_column=data.get('grid_column', 0)
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
    field.grid_column = data.get('grid_column', field.grid_column)
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
    
    # Log the value being read from the database for debugging
    current_app.logger.info(f"Reading settings from database")
    current_app.logger.info(f"SMTP Server: {settings.smtp_server}")
    current_app.logger.info(f"SMTP Port: {settings.smtp_port}")
    current_app.logger.info(f"SMTP Username: {settings.smtp_username}")
    current_app.logger.info(f"TLS Enabled (DB value): {settings.smtp_use_tls}")
    
    # Don't include the password in the response
    # Important: Use appropriate handling for boolean fields
    return jsonify({
        'id': settings.id,
        'smtp_server': settings.smtp_server or '',
        'smtp_port': settings.smtp_port or 25,
        'smtp_username': settings.smtp_username or '',
        'smtp_use_tls': bool(settings.smtp_use_tls),  # Convert to proper boolean
        'smtp_from_email': settings.smtp_from_email or '',
        'smtp_from_name': settings.smtp_from_name or '',
        'notification_emails': settings.notification_emails or '',
        'enable_global_notifications': bool(settings.enable_global_notifications),  # Convert to proper boolean
        'updated_at': settings.updated_at.isoformat() if settings.updated_at else None
    })

@admin_bp.route('/api/admin/settings', methods=['PUT'])
@admin_required
def update_settings():
    """Update settings"""
    settings = Settings.get_settings()
    data = request.json or {}
    
    # Log the incoming data for debugging
    current_app.logger.info(f"Settings update received: {data}")
    
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
    
    # Special handling for boolean TLS setting
    if 'smtp_use_tls' in data:
        tls_value = data['smtp_use_tls']
        # Make sure we convert to proper boolean
        if isinstance(tls_value, bool):
            settings.smtp_use_tls = tls_value
        elif isinstance(tls_value, str):
            settings.smtp_use_tls = tls_value.lower() in ('true', 't', 'yes', 'y', '1')
        elif isinstance(tls_value, int):
            settings.smtp_use_tls = bool(tls_value)
        else:
            current_app.logger.warning(f"Received invalid TLS value: {tls_value} (type: {type(tls_value)})")
        
        # Log the new TLS value
        current_app.logger.info(f"TLS setting updated to: {settings.smtp_use_tls}")
    
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
    settings.updated_by = get_jwt_identity()
    
    db.session.commit()
    
    # Log all settings after update for debugging
    current_app.logger.info(f"Settings updated successfully by {get_jwt().get('email')}")
    current_app.logger.info(f"SMTP Server: {settings.smtp_server}")
    current_app.logger.info(f"SMTP Port: {settings.smtp_port}")
    current_app.logger.info(f"SMTP Username: {settings.smtp_username}")
    current_app.logger.info(f"TLS Enabled: {settings.smtp_use_tls}")
    
    return jsonify({
        'message': 'Settings updated successfully',
        'updated_at': settings.updated_at.isoformat() if settings.updated_at else None
    })

@admin_bp.route('/api/admin/settings/test-email', methods=['POST'])
@admin_required
def test_email():
    """Send a test email using the current settings"""
    from .utils import send_email
    import traceback
    
    data = request.json or {}
    recipient = data.get('email') or get_jwt().get('email')
    
    if not recipient:
        return jsonify({'error': 'No recipient email provided'}), 400
    
    # Get the current settings
    settings = Settings.get_settings()
    
    # Log the SMTP configuration for debugging
    current_app.logger.info(f"Test email requested with SMTP settings:")
    current_app.logger.info(f"Server: {settings.smtp_server}")
    current_app.logger.info(f"Port: {settings.smtp_port}")
    current_app.logger.info(f"Username: {settings.smtp_username}")
    current_app.logger.info(f"TLS Enabled: {settings.smtp_use_tls}")
    current_app.logger.info(f"Password: {'Set' if settings.smtp_password else 'Not set'}")
    
    try:
        send_email(
            subject="Test Email from Violation System",
            recipients=[recipient],
            body="This is a test email from the Violation System to verify that email sending is properly configured.",
            html="<p>This is a test email from the Violation System to verify that email sending is properly configured.</p>"
        )
        return jsonify({'message': f'Test email sent to {recipient}'})
    except Exception as e:
        error_msg = str(e)
        stack_trace = traceback.format_exc()
        current_app.logger.error(f"Error sending test email: {error_msg}")
        current_app.logger.error(f"Stack trace: {stack_trace}")
        
        # Check for common errors and provide helpful responses
        if "Connection refused" in error_msg:
            detailed_msg = (
                "Connection refused error. Possible causes:\n"
                "1. SMTP server address or port may be incorrect\n"
                "2. Firewall may be blocking outgoing connections\n"
                "3. SMTP server may be down or not accepting connections\n"
                f"Error details: {error_msg}"
            )
        elif "Authentication" in error_msg or "credential" in error_msg.lower():
            detailed_msg = (
                "Authentication error. Possible causes:\n"
                "1. Username or password may be incorrect\n"
                "2. Account may require specific security settings\n"
                f"Error details: {error_msg}"
            )
        else:
            detailed_msg = f"Failed to send test email: {error_msg}"
            
        return jsonify({'error': detailed_msg}), 500
