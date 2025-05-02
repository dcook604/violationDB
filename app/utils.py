import os
from flask import current_app, render_template, url_for, g
from werkzeug.utils import secure_filename
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
    """
    Generate a PDF file from HTML content
    
    Args:
        html_content: HTML content to convert to PDF
        pdf_path: Path to save the PDF file
        
    Returns:
        str: Path to the generated PDF file
    """
    try:
        # First attempt: Direct conversion using document.render() for WeasyPrint 61+
        from weasyprint import HTML
        current_app.logger.info(f"Generating PDF at {pdf_path} using WeasyPrint 61+ API")
        
        # Generate HTML document and render
        html = HTML(string=html_content)
        document = html.render()
        
        # Write to PDF file
        with open(pdf_path, 'wb') as pdf_file:
            try:
                document.write_pdf(pdf_file)
                current_app.logger.info(f"Successfully generated PDF ({os.path.getsize(pdf_path)} bytes)")
                return pdf_path
            except TypeError as err:
                if "PDF.__init__() takes 1 positional argument but 3 were given" in str(err):
                    current_app.logger.warning(f"pydyf compatibility issue detected: {err}")
                    # Close the file and use alternative approach
                    pdf_file.close()
                    raise Exception("pydyf compatibility issue - using fallback approach")
                else:
                    raise
            
    except Exception as e:
        current_app.logger.error(f"Error in generate_pdf_from_html (attempt 1): {str(e)}")
        
        # Second attempt: Using a temporary file and command-line tools
        try:
            import tempfile
            import subprocess
            
            current_app.logger.info(f"Trying command-line PDF generation")
            temp_html = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
            
            try:
                # Write HTML to temp file
                with open(temp_html.name, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                # Try using wkhtmltopdf command-line tool if available
                try:
                    cmd = ['/usr/bin/wkhtmltopdf', temp_html.name, pdf_path]
                    current_app.logger.info(f"Executing: {' '.join(cmd)}")
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        current_app.logger.info(f"PDF successfully generated using wkhtmltopdf")
                        return pdf_path
                    else:
                        current_app.logger.error(f"wkhtmltopdf error: {result.stderr}")
                        raise Exception(f"wkhtmltopdf failed: {result.stderr}")
                except (subprocess.SubprocessError, FileNotFoundError) as e:
                    current_app.logger.error(f"Could not use wkhtmltopdf: {str(e)}")
                    raise Exception("Command-line PDF generation failed")
            finally:
                # Clean up temporary file
                if os.path.exists(temp_html.name):
                    os.unlink(temp_html.name)
                    
        except Exception as e2:
            current_app.logger.error(f"Error in generate_pdf_from_html (attempt 2): {str(e2)}")
            raise Exception(f"Failed to generate PDF: {str(e2)}")

def send_email(subject, recipients, body, attachments=None, cc=None, html=None):
    from .models import Settings
    from flask import current_app
    import time
    
    # Get settings from the database
    settings = Settings.get_settings()
    
    # Log the intent to send an email with settings details
    current_app.logger.info(f"Preparing to send email: subject='{subject}', to={recipients}")
    current_app.logger.info(f"SMTP Settings: server={settings.smtp_server}, port={settings.smtp_port}, user={settings.smtp_username}, TLS={settings.smtp_use_tls}")
    
    try:
        # Only apply database settings if they're properly configured
        if settings.smtp_server and settings.smtp_port and settings.smtp_username and settings.smtp_password:
            from flask_mail import Mail, Message
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
            
            # Debug logging - show what we're using (masking password)
            current_app.logger.info(f"Using SMTP: {config['MAIL_SERVER']}:{config['MAIL_PORT']} " +
                              f"with user={config['MAIL_USERNAME']}, " +
                              f"TLS={config['MAIL_USE_TLS']}")
            
            try:
                # Import mail from app
                from . import mail
                
                # Test direct connection to SMTP server before sending
                import socket
                socket_test_start = time.time()
                current_app.logger.info(f"Testing socket connection to {config['MAIL_SERVER']}:{config['MAIL_PORT']}...")
                
                try:
                    sock = socket.create_connection((config['MAIL_SERVER'], config['MAIL_PORT']), timeout=10)
                    sock.close()
                    socket_test_time = time.time() - socket_test_start
                    current_app.logger.info(f"Socket connection successful ({socket_test_time:.2f}s)")
                except Exception as sock_err:
                    current_app.logger.error(f"Socket connection failed: {str(sock_err)}")
                    raise Exception(f"Cannot connect to SMTP server {config['MAIL_SERVER']}:{config['MAIL_PORT']}: {str(sock_err)}")
                
                # Create message with current settings
                msg = Message(subject, recipients=recipients, cc=cc, body=body, html=html)
                attachments = attachments or []
                for att in attachments:
                    with open(att, 'rb') as f:
                        msg.attach(os.path.basename(att), 'application/pdf', f.read())
                
                # Send with mail instance from app context
                mail.send(msg)
                current_app.logger.info("Email sent successfully")
            except Exception as e:
                current_app.logger.error(f"Error sending email with custom SMTP settings: {str(e)}")
                raise
            finally:
                # Restore original config
                current_app.config['MAIL_SERVER'] = original_server
                current_app.config['MAIL_PORT'] = original_port
                current_app.config['MAIL_USERNAME'] = original_username
                current_app.config['MAIL_PASSWORD'] = original_password
                current_app.config['MAIL_USE_TLS'] = original_tls
                current_app.config['MAIL_DEFAULT_SENDER'] = original_sender
        else:
            # Missing required settings
            missing = []
            if not settings.smtp_server:
                missing.append("SMTP Server")
            if not settings.smtp_port:
                missing.append("SMTP Port")
            if not settings.smtp_username:
                missing.append("SMTP Username")
            if not settings.smtp_password:
                missing.append("SMTP Password")
            
            missing_str = ", ".join(missing)
            error_msg = f"Missing required SMTP settings: {missing_str}"
            current_app.logger.error(error_msg)
            raise Exception(error_msg)
    except Exception as e:
        current_app.logger.error(f"Email sending failed: {str(e)}")
        # Re-raise the exception so it can be handled by the caller
        raise

def create_violation_html(violation, field_defs=None):
    """
    Generate an HTML file for a violation record
    
    Args:
        violation: The violation object
        field_defs: Optional list of field definitions
        
    Returns:
        tuple: (html_path, html_content)
    """
    from .models import ViolationFieldValue, FieldDefinition, User, ViolationReply
    
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
    
    # Get violation replies
    replies = ViolationReply.query.filter_by(violation_id=violation.id).order_by(ViolationReply.created_at).all()
    
    # Prepare template data
    template_data = {
        'violation': violation,
        'dynamic_fields': dynamic_fields,
        'field_images': field_images,
        'has_images': has_images,
        'creator': creator,
        'replies': replies
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
        # First attempt: Using WeasyPrint 61+ with document.render() approach
        current_app.logger.info(f"Generating PDF for violation {violation.id} at {pdf_path}")
        from weasyprint import HTML
        
        # Generate HTML document and render
        html = HTML(string=html_content)
        document = html.render()
        
        # Write to PDF file
        with open(pdf_path, 'wb') as pdf_file:
            try:
                document.write_pdf(pdf_file)
                current_app.logger.info(f"Successfully generated PDF ({os.path.getsize(pdf_path)} bytes)")
                return pdf_path
            except TypeError as err:
                if "PDF.__init__() takes 1 positional argument but 3 were given" in str(err):
                    current_app.logger.warning(f"pydyf compatibility issue detected: {err}")
                    # Close the file and use alternative approach
                    pdf_file.close()
                    raise Exception("pydyf compatibility issue - using fallback approach")
                else:
                    raise
                    
    except Exception as e:
        current_app.logger.error(f"PDF generation error (attempt 1): {str(e)}")
        try:
            # Second attempt: Save HTML to temporary file and use a command-line tool
            import tempfile
            import subprocess
            
            current_app.logger.info(f"Attempting command-line PDF generation")
            temp_html = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
            try:
                # Write HTML to temp file
                with open(temp_html.name, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                # Try using wkhtmltopdf command-line tool if available
                try:
                    cmd = ['/usr/bin/wkhtmltopdf', temp_html.name, pdf_path]
                    current_app.logger.info(f"Executing: {' '.join(cmd)}")
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        current_app.logger.info(f"PDF successfully generated using wkhtmltopdf")
                    else:
                        current_app.logger.error(f"wkhtmltopdf error: {result.stderr}")
                        raise Exception(f"wkhtmltopdf failed: {result.stderr}")
                except (subprocess.SubprocessError, FileNotFoundError) as e:
                    current_app.logger.error(f"Could not use wkhtmltopdf: {str(e)}")
                    raise Exception("Command-line PDF generation failed")
            finally:
                # Clean up temporary file
                if os.path.exists(temp_html.name):
                    os.unlink(temp_html.name)
                    
        except Exception as e2:
            current_app.logger.error(f"PDF generation error (attempt 2): {str(e2)}")
            # Final fallback: Create a minimal valid PDF with error message
            try:
                current_app.logger.info("Creating fallback error PDF")
                with open(pdf_path, 'w', encoding='utf-8') as f:
                    f.write(f"""
                    %PDF-1.4
                    1 0 obj
                    << /Type /Catalog
                       /Pages 2 0 R
                    >>
                    endobj
                    2 0 obj
                    << /Type /Pages
                       /Kids [3 0 R]
                       /Count 1
                    >>
                    endobj
                    3 0 obj
                    << /Type /Page
                       /Parent 2 0 R
                       /Resources << /Font << /F1 4 0 R >> >>
                       /MediaBox [0 0 612 792]
                       /Contents 5 0 R
                    >>
                    endobj
                    4 0 obj
                    << /Type /Font
                       /Subtype /Type1
                       /Name /F1
                       /BaseFont /Helvetica
                    >>
                    endobj
                    5 0 obj
                    << /Length 68 >>
                    stream
                    BT
                    /F1 12 Tf
                    100 700 Td
                    (PDF Generation Error - Technical support has been notified) Tj
                    ET
                    endstream
                    endobj
                    xref
                    0 6
                    0000000000 65535 f
                    0000000009 00000 n
                    0000000063 00000 n
                    0000000135 00000 n
                    0000000267 00000 n
                    0000000358 00000 n
                    trailer
                    << /Size 6
                       /Root 1 0 R
                    >>
                    startxref
                    477
                    %%EOF
                    """)
                current_app.logger.info(f"Created fallback PDF at {pdf_path}")
            except Exception as e3:
                current_app.logger.error(f"Failed to create error PDF: {str(e3)}")
    
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
    
    <p>To respond to this violation, please view the full details and use the reply form at the bottom of the page.</p>
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
