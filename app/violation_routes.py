from flask import Blueprint, request, jsonify, current_app, send_from_directory, render_template, abort, send_file, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Violation, FieldDefinition, ViolationFieldValue, ViolationReply
from . import db
import os
import json
from sqlalchemy import text
from werkzeug.utils import secure_filename
import uuid
from .utils import create_violation_html, generate_violation_pdf, send_violation_notification, get_cached_fields, clear_field_cache
import datetime

violation_bp = Blueprint('violations', __name__)

CUSTOM_FIELDS_PATH = os.path.join(os.path.dirname(__file__), 'custom_violation_fields.json')
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def load_custom_fields():
    if not os.path.exists(CUSTOM_FIELDS_PATH):
        return []
    with open(CUSTOM_FIELDS_PATH, 'r') as f:
        return json.load(f)

def save_custom_fields(fields):
    with open(CUSTOM_FIELDS_PATH, 'w') as f:
        json.dump(fields, f, indent=2)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- API Endpoints only below ---

@violation_bp.route('/api/fields', methods=['GET'])
def api_list_fields():
    # Use cached fields to improve performance
    fields = get_cached_fields('all')
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

@violation_bp.route('/api/fields/active', methods=['GET'])
def api_list_active_fields():
    """API endpoint to list only active fields (optimized)"""
    fields = get_cached_fields('active')
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

@violation_bp.route('/api/violations', methods=['POST'])
@login_required
def api_create_violation():
    try:
        data = request.json or {}
        current_app.logger.info(f"Received violation data: {json.dumps(data)}")
        
        # Generate a reference number if not provided
        if not data.get('reference'):
            now = datetime.datetime.now()
            reference = f"VIO-{now.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
            data['reference'] = reference
        
        # Process incident_date to handle empty strings and convert to proper date object
        incident_date = data.get('incident_date')
        if incident_date == '' or incident_date is None:
            incident_date = None
        elif isinstance(incident_date, str):
            try:
                # Try to parse the date string into a datetime object
                incident_date = datetime.datetime.fromisoformat(incident_date.replace('Z', '+00:00')).date()
            except (ValueError, TypeError):
                # If parsing fails, set to None to avoid database errors
                current_app.logger.warning(f"Invalid incident_date format: {incident_date}, setting to None")
                incident_date = None
        
        # Create new violation with better checking of data
        violation = Violation(
            reference=data.get('reference', ''),
            category=data.get('category', ''),
            building=data.get('building', ''),
            unit_number=data.get('unit_number', ''),
            incident_date=incident_date,
            incident_time=data.get('incident_time'),
            subject=data.get('subject', ''),
            details=data.get('details', ''),
            created_by=current_user.id
        )
        
        # Log violation data for debugging
        current_app.logger.info(f"Created violation record: reference={violation.reference}, category={violation.category}")
        
        db.session.add(violation)
        db.session.flush()  # Get the violation ID before commit
        
        # Process dynamic fields
        dynamic_fields = data.get('dynamic_fields', {})
        current_app.logger.info(f"Processing dynamic fields: {json.dumps(dynamic_fields)}")
        
        # Track which fields were processed successfully
        processed_fields = []
        
        for field_name, value in dynamic_fields.items():
            # Use cached field definitions to improve performance
            field_defs = get_cached_fields('active')
            field_def = next((f for f in field_defs if f.name == field_name), None)
            if field_def:
                db.session.add(ViolationFieldValue(
                    violation_id=violation.id,
                    field_definition_id=field_def.id,
                    value=value
                ))
                processed_fields.append(field_name)
            else:
                current_app.logger.warning(f"Field definition not found for: {field_name}")
        
        db.session.commit()
        current_app.logger.info(f"Saved violation {violation.id} with {len(processed_fields)} dynamic fields")
        
        # Generate HTML and PDF for the violation
        try:
            # Get all field definitions for HTML generation, using cache
            field_defs = get_cached_fields('all')
            
            # Create the HTML file
            html_path, html_content = create_violation_html(violation, field_defs)
            current_app.logger.info(f"HTML generated successfully for violation {violation.id}")
            
            # Generate the PDF file
            current_app.logger.info(f"Starting PDF generation for violation {violation.id}")
            pdf_path = generate_violation_pdf(violation, html_content)
            
            # Verify the PDF was created successfully
            if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
                current_app.logger.info(f"PDF generated successfully at {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
            else:
                current_app.logger.error(f"PDF generation issue: file is empty or missing at {pdf_path}")
            
            # Send email notification
            try:
                send_violation_notification(violation, html_path)
                current_app.logger.info(f"Email notification sent for violation {violation.id}")
            except Exception as email_err:
                current_app.logger.error(f"Error sending email notification: {str(email_err)}")
            
            # Store the HTML and PDF paths in the database
            violation.html_path = os.path.relpath(html_path, current_app.config['BASE_DIR'])
            violation.pdf_path = os.path.relpath(pdf_path, current_app.config['BASE_DIR'])
            db.session.commit()
            current_app.logger.info(f"Updated violation record with HTML and PDF paths")
        except Exception as e:
            current_app.logger.error(f"Error in document generation process: {str(e)}")
            import traceback
            current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        
        return jsonify({
            'id': violation.id,
            'message': 'Violation created successfully',
            'processed_fields': processed_fields
        }), 201
    except Exception as e:
        current_app.logger.error(f"Error creating violation: {str(e)}")
        db.session.rollback()
        return jsonify({'error': f'Failed to create violation: {str(e)}'}), 500

@violation_bp.route('/violations/view/<int:vid>')
def view_violation_html(vid):
    """Public route to view a violation in HTML format"""
    violation = Violation.query.get_or_404(vid)
    
    # Check if an HTML file already exists
    html_dir = os.path.join(current_app.config['BASE_DIR'], 'html_violations')
    html_path = os.path.join(html_dir, f'violation_{vid}.html')
    
    # If the file doesn't exist, create it
    if not os.path.exists(html_path):
        try:
            html_path, _ = create_violation_html(violation)
        except Exception as e:
            current_app.logger.error(f"Error generating HTML: {str(e)}")
            abort(500, description="Could not generate HTML view")
    
    # Serve the HTML file
    return send_file(html_path)

@violation_bp.route('/violations/pdf/<int:vid>')
@login_required
def download_violation_pdf(vid):
    """Download the PDF for a violation"""
    violation = Violation.query.get_or_404(vid)
    
    # Only allow access if admin or owner
    if not (current_user.is_admin or violation.created_by == current_user.id):
        abort(403)
    
    # Check if a PDF file already exists
    pdf_dir = os.path.join(current_app.config['BASE_DIR'], 'pdf_violations')
    pdf_path = os.path.join(pdf_dir, f'violation_{vid}.pdf')
    
    # If the file doesn't exist or is empty, create it
    if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) == 0:
        try:
            current_app.logger.info(f"Generating PDF for violation {vid}")
            pdf_path = generate_violation_pdf(violation)
            
            # Verify the PDF was generated and is not empty
            if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) == 0:
                current_app.logger.error(f"Generated PDF is empty or missing: {pdf_path}")
                abort(500, description="Could not generate valid PDF")
        except Exception as e:
            current_app.logger.error(f"Error generating PDF: {str(e)}")
            abort(500, description="Could not generate PDF")
    
    # Serve the PDF file
    try:
        return send_file(
            pdf_path, 
            download_name=f"violation_{violation.reference}.pdf",
            as_attachment=True,
            mimetype='application/pdf'
        )
    except Exception as e:
        current_app.logger.error(f"Error sending PDF file: {str(e)}")
        abort(500, description="Error delivering PDF file")

@violation_bp.route('/api/violations/<int:vid>/upload', methods=['POST'])
@login_required
def api_upload_files(vid):
    violation = Violation.query.get_or_404(vid)
    if not (current_user.is_admin or violation.created_by == current_user.id):
        return jsonify({'error': 'Forbidden'}), 403
    
    if 'files' not in request.files:
        return jsonify({'error': 'No files part'}), 400
    
    files = request.files.getlist('files')
    if not files or files[0].filename == '':
        return jsonify({'error': 'No files selected'}), 400
    
    field_name = request.form.get('field_name')
    if not field_name:
        return jsonify({'error': 'Field name is required'}), 400
    
    # Get the field definition to check validation rules, using cached fields
    all_fields = get_cached_fields('all')
    field_def = next((f for f in all_fields if f.name == field_name), None)
    if not field_def:
        return jsonify({'error': 'Field not found'}), 404
    
    # Check validation rules
    max_files = 5
    max_size_mb = 5
    
    if field_def.validation:
        try:
            validation = json.loads(field_def.validation)
            max_files = validation.get('maxFiles', 5)
            max_size_mb = validation.get('maxSizePerFile', 5)
        except Exception as e:
            current_app.logger.error(f"Error parsing validation rules: {str(e)}")
    
    if len(files) > max_files:
        return jsonify({'error': f'Maximum of {max_files} files allowed'}), 400
    
    # Create folder for this violation if it doesn't exist
    violation_folder = os.path.join(UPLOAD_FOLDER, f'violation_{vid}')
    os.makedirs(violation_folder, exist_ok=True)
    
    # Save files and record paths
    saved_files = []
    max_size_bytes = max_size_mb * 1024 * 1024
    
    for file in files:
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only jpg, jpeg, png, and gif are allowed'}), 400
        
        if file.content_length and file.content_length > max_size_bytes:
            return jsonify({'error': f'File too large. Maximum size is {max_size_mb}MB'}), 400
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{extension}"
        
        file_path = os.path.join(violation_folder, unique_filename)
        file.save(file_path)
        
        # Store the path relative to the upload folder
        relative_path = os.path.join(f'violation_{vid}', unique_filename)
        saved_files.append(relative_path)
    
    # Store the file paths in the database
    field_value = ViolationFieldValue.query.filter_by(
        violation_id=vid,
        field_definition_id=field_def.id
    ).first()
    
    if field_value:
        # Append to existing files if any
        existing_files = field_value.value.split(',') if field_value.value else []
        field_value.value = ','.join(existing_files + saved_files)
    else:
        # Create new field value
        db.session.add(ViolationFieldValue(
            violation_id=vid,
            field_definition_id=field_def.id,
            value=','.join(saved_files)
        ))
    
    db.session.commit()
    
    # Regenerate the HTML and PDF after adding files
    try:
        html_path, html_content = create_violation_html(violation)
        pdf_path = generate_violation_pdf(violation, html_content)
    except Exception as e:
        current_app.logger.error(f"Error updating violation files after upload: {str(e)}")
    
    return jsonify({
        'message': 'Files uploaded successfully',
        'files': saved_files
    })

@violation_bp.route('/uploads/<path:filename>')
def get_uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@violation_bp.route('/api/violations', methods=['GET'])
@login_required
def api_list_violations():
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        date_filter = request.args.get('date_filter', None, type=str)  # 'last7days', 'last30days', or None
        
        # Special handling for dashboard which uses limit parameter
        limit = request.args.get('limit', None, type=int)
        if limit is not None:
            # If limit is specified, use it as per_page and set page to 1
            per_page = limit
            page = 1
        
        # Calculate offset for pagination
        offset = (page - 1) * per_page
        
        # Base SQL query
        if current_user.is_admin:
            sql = "SELECT id, reference, category, building, unit_number, created_at, created_by, subject, details, html_path, pdf_path FROM violations"
        else:
            sql = "SELECT id, reference, category, building, unit_number, created_at, created_by, subject, details, html_path, pdf_path FROM violations WHERE created_by = :user_id"
        
        # Add date filter conditions if specified
        params = {"user_id": current_user.id}
        
        if date_filter:
            current_app.logger.info(f"Applying date filter: {date_filter}")
            from datetime import datetime, timedelta
            today = datetime.now().date()
            
            if date_filter == 'last7days':
                # Last 7 days
                seven_days_ago = (today - timedelta(days=7)).isoformat()
                sql += " AND DATE(created_at) >= :start_date"
                params["start_date"] = seven_days_ago
            elif date_filter == 'last30days':
                # Last 30 days
                thirty_days_ago = (today - timedelta(days=30)).isoformat()
                sql += " AND DATE(created_at) >= :start_date"
                params["start_date"] = thirty_days_ago
        
        # Add total count query
        count_sql = sql.replace("SELECT id, reference, category, building, unit_number, created_at, created_by, subject, details, html_path, pdf_path", "SELECT COUNT(*) as total")
        
        # Add ordering and pagination to main query
        sql += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
        params["limit"] = per_page
        params["offset"] = offset
            
        # Execute count query
        count_result = db.session.execute(text(count_sql), params)
        total_count = count_result.fetchone().total
        
        # Calculate total pages
        total_pages = (total_count + per_page - 1) // per_page  # Ceiling division
            
        # Execute main query
        result = db.session.execute(text(sql), params)
        
        # Process results
        violations = []
        for row in result:
            # Safely handle created_at which might be a string or datetime
            created_at = None
            try:
                if isinstance(row.created_at, str):
                    created_at = row.created_at
                elif row.created_at:
                    created_at = row.created_at.isoformat()
            except Exception as err:
                current_app.logger.warning(f"Error formatting created_at: {str(err)}")
                created_at = str(row.created_at) if row.created_at else None
                
            violation = {
                'id': row.id,
                'reference': row.reference or '',
                'category': row.category or '',
                'building': row.building or '',
                'unit_number': row.unit_number or '',
                'created_at': created_at,
                'created_by': row.created_by,
                'subject': row.subject or '',
                'details': row.details or '',
                'html_path': f"/violations/view/{row.id}" if row.html_path else None,
                'pdf_path': f"/violations/pdf/{row.id}" if row.pdf_path else None,
                'dynamic_fields': {}
            }
            
            # Fetch dynamic fields for this violation
            try:
                field_values = ViolationFieldValue.query.filter_by(violation_id=row.id).all()
                dynamic_fields = {}
                
                for fv in field_values:
                    field = FieldDefinition.query.get(fv.field_definition_id)
                    if field:
                        dynamic_fields[field.name] = fv.value
                        
                violation['dynamic_fields'] = dynamic_fields
            except Exception as field_err:
                current_app.logger.warning(f"Error fetching dynamic fields for violation {row.id}: {str(field_err)}")
            
            violations.append(violation)
            
        # For dashboard compatibility (limit parameter), return just the violations array
        if limit is not None:
            return jsonify(violations)
        
        # Return data with pagination info for regular violations list
        return jsonify({
            'violations': violations,
            'pagination': {
                'total': total_count,
                'page': page,
                'per_page': per_page,
                'pages': total_pages
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching violations: {str(e)}")
        return jsonify({'violations': [], 'pagination': {'total': 0, 'page': 1, 'per_page': 10, 'pages': 0}})

@violation_bp.route('/api/violations/<int:vid>', methods=['GET'])
@login_required
def api_violation_detail(vid):
    v = Violation.query.get_or_404(vid)
    if not (current_user.is_admin or v.created_by == current_user.id):
        return jsonify({'error': 'Forbidden'}), 403
    field_values = ViolationFieldValue.query.filter_by(violation_id=v.id).all()
    dynamic_fields = {}
    for fv in field_values:
        field = FieldDefinition.query.get(fv.field_definition_id)
        if field:
            dynamic_fields[field.name] = fv.value
            
    # Safely handle created_at which might be a string or datetime
    created_at = None
    try:
        if hasattr(v, 'created_at'):
            if isinstance(v.created_at, str):
                created_at = v.created_at
            elif v.created_at:
                created_at = v.created_at.isoformat()
    except Exception as err:
        current_app.logger.warning(f"Error formatting created_at for violation {v.id}: {str(err)}")
        created_at = str(v.created_at) if hasattr(v, 'created_at') and v.created_at else None
            
    # Safely handle incident_date which might be a string or datetime
    incident_date = None
    try:
        if v.incident_date:
            if isinstance(v.incident_date, str):
                incident_date = v.incident_date
            else:
                incident_date = v.incident_date.isoformat()
    except Exception as err:
        current_app.logger.warning(f"Error formatting incident_date for violation {v.id}: {str(err)}")
        incident_date = str(v.incident_date) if v.incident_date else None
            
    result = {
        'id': v.id,
        'reference': v.reference,
        'category': v.category,
        'building': v.building,
        'unit_number': v.unit_number,
        'incident_date': incident_date,
        'subject': v.subject,
        'details': v.details,
        'created_at': created_at,
        'created_by': v.created_by,
        'dynamic_fields': dynamic_fields,
        'html_path': f"/violations/view/{v.id}" if hasattr(v, 'html_path') and v.html_path else None,
        'pdf_path': f"/violations/pdf/{v.id}" if hasattr(v, 'pdf_path') and v.pdf_path else None
    }
    return jsonify(result)

@violation_bp.route('/api/violations/<int:vid>', methods=['PUT'])
@login_required
def api_edit_violation(vid):
    v = Violation.query.get_or_404(vid)
    if not (current_user.is_admin or v.created_by == current_user.id):
        return jsonify({'error': 'Forbidden'}), 403
    data = request.json or {}
    for field in ['category', 'building', 'unit_number', 'incident_date', 'subject', 'details']:
        if field in data:
            setattr(v, field, data[field])
    dynamic_fields = data.get('dynamic_fields', {})
    for name, value in dynamic_fields.items():
        field_def = FieldDefinition.query.filter_by(name=name).first()
        if field_def:
            vfv = ViolationFieldValue.query.filter_by(violation_id=v.id, field_definition_id=field_def.id).first()
            if vfv:
                vfv.value = value
            else:
                db.session.add(ViolationFieldValue(
                    violation_id=v.id,
                    field_definition_id=field_def.id,
                    value=value
                ))
    db.session.commit()
    
    # Regenerate HTML and PDF files after update
    try:
        html_path, html_content = create_violation_html(v)
        pdf_path = generate_violation_pdf(v, html_content)
    except Exception as e:
        current_app.logger.error(f"Error updating violation files after edit: {str(e)}")
    
    return jsonify({'success': True})

@violation_bp.route('/api/violations/<int:vid>', methods=['DELETE'])
@login_required
def api_delete_violation(vid):
    v = Violation.query.get_or_404(vid)
    if not (current_user.is_admin or v.created_by == current_user.id):
        return jsonify({'error': 'Forbidden'}), 403
    ViolationFieldValue.query.filter_by(violation_id=v.id).delete()
    db.session.delete(v)
    db.session.commit()
    return jsonify({'success': True})

@violation_bp.route('/api/violations/<int:vid>/fields', methods=['GET'])
def api_violation_field_values(vid):
    values = ViolationFieldValue.query.filter_by(violation_id=vid).all()
    return jsonify([{
        'field_definition_id': v.field_definition_id,
        'value': v.value
    } for v in values])

@violation_bp.route('/violations/<int:vid>/reply', methods=['POST'])
def submit_violation_reply(vid):
    """Handle replies submitted via the HTML view"""
    from .models import ViolationReply
    
    violation = Violation.query.get_or_404(vid)
    
    # Get form data
    email = request.form.get('email')
    response_text = request.form.get('response_text')
    
    if not email or not response_text:
        flash('Email and response are required.')
        return redirect(url_for('violations.view_violation_html', vid=vid))
    
    # Create new reply
    reply = ViolationReply(
        violation_id=vid,
        email=email,
        response_text=response_text,
        ip_address=request.remote_addr
    )
    
    db.session.add(reply)
    db.session.commit()
    
    # Regenerate HTML after adding reply
    try:
        html_path, html_content = create_violation_html(violation)
        pdf_path = generate_violation_pdf(violation, html_content)
        
        # Store the updated HTML and PDF paths
        violation.html_path = os.path.relpath(html_path, current_app.config['BASE_DIR'])
        violation.pdf_path = os.path.relpath(pdf_path, current_app.config['BASE_DIR'])
        db.session.commit()
        
        # Send notification about the new reply
        try:
            notify_about_reply(reply)
        except Exception as e:
            current_app.logger.error(f"Error sending reply notification: {str(e)}")
    
    except Exception as e:
        current_app.logger.error(f"Error regenerating files after reply: {str(e)}")
    
    flash('Your response has been recorded.')
    return redirect(url_for('violations.view_violation_html', vid=vid))

def notify_about_reply(reply):
    """Send notification about a new violation reply"""
    from .models import User, Settings
    
    # Get the violation
    violation = Violation.query.get(reply.violation_id)
    if not violation:
        current_app.logger.error(f"Violation {reply.violation_id} not found for reply notification")
        return False
    
    # Get the creator
    creator = None
    if violation.created_by:
        creator = User.query.get(violation.created_by)
    
    # Get email recipients (creator + global notifications)
    recipients = []
    
    # Add creator email if available
    if creator and creator.email:
        recipients.append(creator.email)
    
    # Add global notification emails
    settings = Settings.get_settings()
    if settings.enable_global_notifications and settings.notification_emails:
        global_emails = settings.get_notification_emails_list()
        recipients.extend(global_emails)
    
    # Remove duplicates
    recipients = list(dict.fromkeys(recipients))
    
    if not recipients:
        current_app.logger.info(f"No recipients for reply notification on violation {violation.id}")
        return False
    
    # Prepare email
    subject = f"New Response to Violation {violation.reference}"
    view_url = f"{current_app.config.get('BASE_URL', 'http://localhost:5004')}/violations/view/{violation.id}"
    
    # Email body
    body_text = f"""A new response has been added to violation {violation.reference}.

From: {reply.email}
Date: {reply.created_at.strftime('%Y-%m-%d %H:%M:%S')}

Response:
{reply.response_text}

You can view the full details at:
{view_url}
"""
    
    # Using a regular string instead of f-string to avoid backslash issues
    html_body = """
    <p>A new response has been added to violation {reference}.</p>
    
    <p><strong>From:</strong> {email}<br>
    <strong>Date:</strong> {date}</p>
    
    <p><strong>Response:</strong><br>
    {response_br}</p>
    
    <p>You can view the full details by <a href="{url}">clicking here</a>.</p>
    """
    
    # Format the string separately
    response_with_br = reply.response_text.replace('\n', '<br>')
    html_body = html_body.format(
        reference=violation.reference,
        email=reply.email,
        date=reply.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        response_br=response_with_br,
        url=view_url
    )
    
    # Send the email
    try:
        from .utils import send_email
        send_email(
            subject=subject,
            recipients=recipients,
            body=body_text,
            html=html_body
        )
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending reply notification email: {str(e)}")
        return False
