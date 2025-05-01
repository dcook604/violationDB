import os
from flask import current_app, render_template, url_for, g
from werkzeug.utils import secure_filename
from weasyprint import HTML
from flask_mail import Message
from . import mail
import json
from urllib.parse import urljoin
import time

# Cache for field definitions
_field_cache = {
    'all': {'data': None, 'timestamp': 0},
    'active': {'data': None, 'timestamp': 0},
    'email': {'data': None, 'timestamp': 0}
}
# Cache expiration time in seconds (5 minutes)
CACHE_EXPIRATION = 300

def get_cached_fields(cache_key='all', filter_func=None, force_refresh=False):
    """
    Get cached field definitions or fetch from database if cache is expired
    
    Args:
        cache_key (str): Cache key to use ('all', 'active', 'email')
        filter_func (function): Optional filter function to apply to fields
        force_refresh (bool): Force a refresh of the cache
        
    Returns:
        list: Field definitions
    """
    from .models import FieldDefinition
    
    now = time.time()
    cache = _field_cache.get(cache_key, {'data': None, 'timestamp': 0})
    
    # If cache is expired or force refresh, fetch from database
    if force_refresh or not cache['data'] or (now - cache['timestamp'] > CACHE_EXPIRATION):
        if cache_key == 'active':
            fields = FieldDefinition.query.filter_by(active=True).order_by(FieldDefinition.order).all()
        elif cache_key == 'email':
            fields = FieldDefinition.query.filter_by(type='email').all()
        else:
            fields = FieldDefinition.query.order_by(FieldDefinition.order).all()
        
        # Apply custom filter if provided
        if filter_func:
            fields = list(filter(filter_func, fields))
        
        # Update cache
        _field_cache[cache_key] = {
            'data': fields,
            'timestamp': now
        }
        
    return _field_cache[cache_key]['data']

def clear_field_cache():
    """Clear all field definition caches"""
    global _field_cache
    _field_cache = {
        'all': {'data': None, 'timestamp': 0},
        'active': {'data': None, 'timestamp': 0},
        'email': {'data': None, 'timestamp': 0}
    }

def save_uploaded_file(file_storage, folder):
    filename = secure_filename(file_storage.filename)
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder, filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    file_storage.save(path)
    return os.path.relpath(path, current_app.root_path)

def generate_pdf_from_html(html_content, pdf_path):
    HTML(string=html_content).write_pdf(pdf_path)
    return pdf_path

def send_email(subject, recipients, body, attachments=None, cc=None, html=None):
    from .models import Settings
    
    # Get settings from the database
    settings = Settings.get_settings()
    
    # Create a temporary mail instance with settings from the database if they exist
    if settings.smtp_server:
        from flask_mail import Mail, Message
        from flask import current_app
        import copy
        
        # Create a copy of the current app config
        config = copy.deepcopy(current_app.config)
        
        # Override with settings from database
        config['MAIL_SERVER'] = settings.smtp_server
        config['MAIL_PORT'] = settings.smtp_port
        config['MAIL_USERNAME'] = settings.smtp_username
        config['MAIL_PASSWORD'] = settings.smtp_password
        config['MAIL_USE_TLS'] = settings.smtp_use_tls
        if settings.smtp_from_email:
            config['MAIL_DEFAULT_SENDER'] = settings.smtp_from_name + ' <' + settings.smtp_from_email + '>' if settings.smtp_from_name else settings.smtp_from_email
        
        # Store original config values
        original_server = current_app.config.get('MAIL_SERVER')
        original_port = current_app.config.get('MAIL_PORT')
        original_username = current_app.config.get('MAIL_USERNAME')
        original_password = current_app.config.get('MAIL_PASSWORD')
        original_tls = current_app.config.get('MAIL_USE_TLS')
        original_sender = current_app.config.get('MAIL_DEFAULT_SENDER')
        
        # Set config to use database settings
        current_app.config['MAIL_SERVER'] = config['MAIL_SERVER']
        current_app.config['MAIL_PORT'] = config['MAIL_PORT']
        current_app.config['MAIL_USERNAME'] = config['MAIL_USERNAME']
        current_app.config['MAIL_PASSWORD'] = config['MAIL_PASSWORD']
        current_app.config['MAIL_USE_TLS'] = config['MAIL_USE_TLS']
        current_app.config['MAIL_DEFAULT_SENDER'] = config.get('MAIL_DEFAULT_SENDER', original_sender)
        
        try:
            # Create message with current settings
            msg = Message(subject, recipients=recipients, cc=cc, body=body, html=html)
            attachments = attachments or []
            for att in attachments:
                with open(att, 'rb') as f:
                    msg.attach(os.path.basename(att), 'application/pdf', f.read())
            
            # Send with mail instance from app context
            mail.send(msg)
        finally:
            # Restore original config
            current_app.config['MAIL_SERVER'] = original_server
            current_app.config['MAIL_PORT'] = original_port
            current_app.config['MAIL_USERNAME'] = original_username
            current_app.config['MAIL_PASSWORD'] = original_password
            current_app.config['MAIL_USE_TLS'] = original_tls
            current_app.config['MAIL_DEFAULT_SENDER'] = original_sender
    else:
        # Use the default mail configuration
        from flask_mail import Message
        from . import mail
        
        msg = Message(subject, recipients=recipients, cc=cc, body=body, html=html)
        attachments = attachments or []
        for att in attachments:
            with open(att, 'rb') as f:
                msg.attach(os.path.basename(att), 'application/pdf', f.read())
        mail.send(msg)

def create_violation_html(violation, field_defs=None):
    """
    Generate an HTML file for a violation record
    
    Args:
        violation: The violation object
        field_defs: Optional list of field definitions
        
    Returns:
        tuple: (html_path, html_content)
    """
    from .models import ViolationFieldValue, FieldDefinition, User
    
    # Create directory for HTML files if it doesn't exist
    html_dir = os.path.join(current_app.config['BASE_DIR'], 'html_violations')
    os.makedirs(html_dir, exist_ok=True)
    
    # Get dynamic field values
    field_values = ViolationFieldValue.query.filter_by(violation_id=violation.id).all()
    
    # Fetch field definitions if not provided, using cache
    if not field_defs:
        field_defs = get_cached_fields('all')
    
    # Create field definition lookup
    field_dict = {fd.id: fd for fd in field_defs}
    
    # Process field values into a dictionary
    dynamic_fields = {}
    field_images = {}
    has_images = False
    
    for fv in field_values:
        field_def = field_dict.get(fv.field_definition_id)
        if field_def:
            dynamic_fields[field_def.name] = fv.value
            
            # Process file fields
            if field_def.type == 'file' and fv.value:
                images = []
                for img_path in fv.value.split(','):
                    if img_path.strip():
                        # Create absolute URL for the image
                        img_url = urljoin(
                            current_app.config.get('BASE_URL', 'http://localhost:5004'),
                            f'/uploads/{img_path}'
                        )
                        images.append(img_url)
                
                if images:
                    field_images[field_def.name] = images
                    has_images = True
    
    # Get creator information
    creator = None
    if violation.created_by:
        creator = User.query.get(violation.created_by)
    
    # Prepare template data
    template_data = {
        'violation': violation,
        'dynamic_fields': dynamic_fields,
        'field_images': field_images,
        'has_images': has_images,
        'creator': creator
    }
    
    # Render the template
    html_content = render_template('violations/detail.html', **template_data)
    
    # Save the HTML content to a file
    html_filename = f'violation_{violation.id}.html'
    html_path = os.path.join(html_dir, html_filename)
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return html_path, html_content

def generate_violation_pdf(violation, html_content=None):
    """
    Generate a PDF file for a violation record
    
    Args:
        violation: The violation object
        html_content: Optional HTML content to use
        
    Returns:
        str: Path to the generated PDF file
    """
    # Create directory for PDF files if it doesn't exist
    pdf_dir = os.path.join(current_app.config['BASE_DIR'], 'pdf_violations')
    os.makedirs(pdf_dir, exist_ok=True)
    
    # Generate HTML content if not provided
    if not html_content:
        _, html_content = create_violation_html(violation)
    
    # Define PDF path
    pdf_filename = f'violation_{violation.id}.pdf'
    pdf_path = os.path.join(pdf_dir, pdf_filename)
    
    try:
        # Generate PDF from HTML using the more compatible approach
        document = HTML(string=html_content)
        document.write_pdf(pdf_path)
    except Exception as e:
        # If there are parameter issues, try a simpler approach
        current_app.logger.error(f"PDF generation error (attempt 1): {str(e)}")
        try:
            from weasyprint import HTML as WPHTML
            WPHTML(string=html_content).write_pdf(target=pdf_path)
        except Exception as e2:
            current_app.logger.error(f"PDF generation error (attempt 2): {str(e2)}")
            # Create an empty file to ensure the path exists
            with open(pdf_path, 'w') as f:
                f.write("PDF generation failed - this is a placeholder file")
    
    return pdf_path

def send_violation_notification(violation, html_path):
    """
    Send email notification about a new violation
    
    Args:
        violation: The violation object
        html_path: Path to the HTML file
    """
    from .models import ViolationFieldValue, FieldDefinition, User, Settings
    
    # Get all email fields from the violation
    email_addresses = []
    
    # Get field definitions for email type, using cache
    email_fields = get_cached_fields('email')
    
    if email_fields:
        for field in email_fields:
            # Get the value for this field in the violation
            field_value = ViolationFieldValue.query.filter_by(
                violation_id=violation.id,
                field_definition_id=field.id
            ).first()
            
            if field_value and field_value.value and '@' in field_value.value:
                email_addresses.append(field_value.value)
    
    # Add global notification emails from settings
    settings = Settings.get_settings()
    if settings.enable_global_notifications and settings.notification_emails:
        global_emails = settings.get_notification_emails_list()
        email_addresses.extend(global_emails)
    
    # Remove duplicates while preserving order
    email_addresses = list(dict.fromkeys(email_addresses))
    
    # If no email addresses were found, return early
    if not email_addresses:
        current_app.logger.info(f"No email addresses found for violation {violation.id}")
        return False
    
    # Get the creator
    creator = None
    if violation.created_by:
        creator = User.query.get(violation.created_by)
    
    # Prepare the email
    subject = f"New Violation Report: {violation.reference}"
    
    # Generate the email body
    body_text = f"""A new violation has been recorded.

Reference: {violation.reference}
Category: {violation.category}
Subject: {violation.subject}

You can view the full details using the link below:
{current_app.config.get('BASE_URL', 'http://localhost:5004')}/violations/view/{violation.id}

Please do not reply to this email.
"""
    
    # Send the email with a link to the HTML view
    view_url = f"{current_app.config.get('BASE_URL', 'http://localhost:5004')}/violations/view/{violation.id}"
    
    html_body = f"""
    <p>A new violation has been recorded.</p>
    <p><strong>Reference:</strong> {violation.reference}<br>
    <strong>Category:</strong> {violation.category}<br>
    <strong>Subject:</strong> {violation.subject}</p>
    
    <p>You can view the full details by <a href="{view_url}">clicking here</a>.</p>
    
    <p>Please do not reply to this email.</p>
    """
    
    try:
        send_email(
            subject=subject,
            recipients=email_addresses,
            body=body_text,
            html=html_body
        )
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending notification email: {str(e)}")
        return False
