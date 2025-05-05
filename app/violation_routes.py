from flask import Blueprint, request, jsonify, current_app, send_from_directory, render_template, abort, send_file, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Violation, FieldDefinition, ViolationFieldValue, ViolationReply, ViolationStatusLog
from . import db
import os
import json
from sqlalchemy import text
from werkzeug.utils import secure_filename
import uuid
from .utils import create_violation_html, generate_violation_pdf, send_violation_notification, get_cached_fields, clear_field_cache, secure_handle_uploaded_file, generate_secure_access_token, validate_secure_access_token, log_violation_access
import datetime

violation_bp = Blueprint('violations', __name__)

CUSTOM_FIELDS_PATH = os.path.join(os.path.dirname(__file__), 'custom_violation_fields.json')
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf', 'docx', 'xlsx', 'txt'}  # Must match allowed MIME types in utils.py

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
        
        # Extract owner/property manager name fields if provided in nested format
        owner_first_name = None
        owner_last_name = None
        tenant_first_name = None
        tenant_last_name = None
        
        if 'owner_property_manager_name' in data and isinstance(data['owner_property_manager_name'], dict):
            owner_first_name = data['owner_property_manager_name'].get('first', '')
            owner_last_name = data['owner_property_manager_name'].get('last', '')
        
        # Extract tenant name fields if provided in nested format
        if 'tenant_name' in data and isinstance(data['tenant_name'], dict):
            tenant_first_name = data['tenant_name'].get('first', '')
            tenant_last_name = data['tenant_name'].get('last', '')
        
        # Create new violation with better checking of data
        violation_data = {
            'reference': data.get('reference', ''),
            'category': data.get('violation_category', data.get('category', '')),
            'building': data.get('building', ''),
            'unit_number': data.get('unit_no', data.get('unit_number', '')),
            'incident_date': incident_date,
            'incident_time': data.get('time', data.get('incident_time', '')),
            'subject': data.get('subject', ''),
            'details': data.get('details', ''),
            'created_by': current_user.id,
            'status': data.get('status', 'Open'),
            
            # Static Violation Fields
            'owner_property_manager_first_name': owner_first_name,
            'owner_property_manager_last_name': owner_last_name,
            'owner_property_manager_email': data.get('owner_property_manager_email', ''),
            'owner_property_manager_telephone': data.get('owner_property_manager_telephone', ''),
            'where_did': data.get('where_did', ''),
            'was_security_or_police_called': data.get('was_security_or_police_called', ''),
            'fine_levied': data.get('fine_levied', ''),
            'action_taken': data.get('action_taken', ''),
            'tenant_first_name': tenant_first_name,
            'tenant_last_name': tenant_last_name,
            'tenant_email': data.get('tenant_email', ''),
            'tenant_phone': data.get('tenant_phone', ''),
            'concierge_shift': data.get('concierge_shift', ''),
            'noticed_by': data.get('noticed_by', ''),
            'people_called': data.get('people_called', ''),
            'actioned_by': data.get('actioned_by', ''),
            'people_involved': data.get('people_involved', ''),
            'incident_details': data.get('incident_details', '')
        }
        
        # Generate a UUID for public_id if the column exists
        try:
            violation = Violation(**violation_data)
            db.session.add(violation)
            db.session.flush()  # Get the violation ID before commit
        except Exception as e:
            # If there's an error with public_id, try without it
            if 'public_id' in str(e):
                current_app.logger.warning(f"Error with public_id field, creating violation without it: {str(e)}")
                # Create without public_id if the column doesn't exist yet
                violation = Violation(**{k: v for k, v in violation_data.items() if k != 'public_id'})
                db.session.add(violation)
                db.session.flush()  # Get the violation ID before commit
            else:
                raise  # Re-raise if it's not related to public_id
        
        # Log violation data for debugging
        current_app.logger.info(f"Created violation record: reference={violation.reference}, category={violation.category}")
        
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
        
        # Process file attachments if present
        attach_evidence = data.get('attach_evidence', [])
        if attach_evidence and isinstance(attach_evidence, list) and len(attach_evidence) > 0:
            current_app.logger.info(f"Processing {len(attach_evidence)} attachments")
            violation.attach_evidence = json.dumps([file.get('name', '') for file in attach_evidence])
        
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
            'public_id': violation.public_id if hasattr(violation, 'public_id') else None,
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
    if not violation.html_path:
        try:
            # Generate a new HTML file if it doesn't exist
            html_path, _ = create_violation_html(violation)
            if not html_path:
                abort(500)  # Internal Server Error
        except Exception as e:
            current_app.logger.error(f"Error generating HTML for violation {vid}: {str(e)}")
            abort(500)  # Internal Server Error
    else:
        # Get the directory and filename
        html_full_path = os.path.join(current_app.config['BASE_DIR'], violation.html_path)
        if not os.path.exists(html_full_path):
            try:
                # Re-generate if the file doesn't exist at the stored path
                html_path, _ = create_violation_html(violation)
                if not html_path:
                    abort(500)  # Internal Server Error
            except Exception as e:
                current_app.logger.error(f"Error regenerating HTML for violation {vid}: {str(e)}")
                abort(500)  # Internal Server Error
    
    # Get the directory and filename from the path
    html_dir = os.path.dirname(os.path.join(current_app.config['BASE_DIR'], violation.html_path))
    html_filename = os.path.basename(violation.html_path)
    
    # Serve the file
    return send_from_directory(html_dir, html_filename)

@violation_bp.route('/violations/pdf/<int:vid>')
@login_required
def download_violation_pdf(vid):
    """Download a violation PDF - requires authentication"""
    violation = Violation.query.get_or_404(vid)
    
    # Check if the user has permission to view this violation
    if not (current_user.is_admin or violation.created_by == current_user.id):
        return jsonify({'error': 'Forbidden'}), 403
    
    # Check if a PDF file already exists
    if not violation.pdf_path:
        try:
            # Generate the HTML first if needed
            if not violation.html_path:
                html_path, html_content = create_violation_html(violation)
            else:
                # Read the existing HTML content
                html_full_path = os.path.join(current_app.config['BASE_DIR'], violation.html_path)
                if os.path.exists(html_full_path):
                    with open(html_full_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                else:
                    # Re-generate HTML if file is missing
                    html_path, html_content = create_violation_html(violation)
            
            # Generate the PDF using the HTML content
            pdf_path = generate_violation_pdf(violation, html_content)
            if not pdf_path:
                abort(500)  # Internal Server Error
        except Exception as e:
            current_app.logger.error(f"Error generating PDF for violation {vid}: {str(e)}")
            abort(500)  # Internal Server Error
    else:
        # Check if the file exists at the stored path
        pdf_full_path = os.path.join(current_app.config['BASE_DIR'], violation.pdf_path)
        if not os.path.exists(pdf_full_path):
            try:
                # Re-generate if the file doesn't exist
                if not violation.html_path:
                    html_path, html_content = create_violation_html(violation)
                else:
                    # Read the existing HTML content
                    html_full_path = os.path.join(current_app.config['BASE_DIR'], violation.html_path)
                    if os.path.exists(html_full_path):
                        with open(html_full_path, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                    else:
                        # Re-generate HTML if file is missing
                        html_path, html_content = create_violation_html(violation)
                
                # Generate the PDF using the HTML content
                pdf_path = generate_violation_pdf(violation, html_content)
                if not pdf_path:
                    abort(500)  # Internal Server Error
            except Exception as e:
                current_app.logger.error(f"Error regenerating PDF for violation {vid}: {str(e)}")
                abort(500)  # Internal Server Error
    
    # Get the directory and filename from the path
    pdf_dir = os.path.dirname(os.path.join(current_app.config['BASE_DIR'], violation.pdf_path))
    pdf_filename = os.path.basename(violation.pdf_path)
    
    # Serve the file
    return send_from_directory(
        pdf_dir,
        pdf_filename,
        as_attachment=True,
        download_name=f"violation_{violation.reference}.pdf"
    )

@violation_bp.route('/api/violations/<int:vid>/upload', methods=['POST'])
@login_required
def api_upload_files(vid):
    """Handle file uploads for a violation with virus scanning"""
    try:
        # Get the violation
        violation = Violation.query.get_or_404(vid)
        
        # Check if the user has permission to modify this violation
        if not (current_user.is_admin or violation.created_by == current_user.id):
            return jsonify({'error': 'Forbidden'}), 403
        
        # Get the field name from query parameters
        field_name = request.args.get('field')
        if not field_name:
            return jsonify({'error': 'No field name provided'}), 400
        
        # Get the field definition
        field_def = FieldDefinition.query.filter_by(name=field_name).first()
        if not field_def:
            return jsonify({'error': f'Field definition not found for {field_name}'}), 404
        
        # Check if there are files in the request
        if 'files' not in request.files:
            return jsonify({'error': 'No files in request'}), 400
        
        # Process each file
        saved_files = []
        file_results = []
        errors = []
        
        for file in request.files.getlist('files'):
            if not file or not file.filename:
                continue
                
            if not allowed_file(file.filename):
                errors.append(f"File {file.filename} has an invalid file type")
                continue
            
            # Use the secure file handling function with virus scanning
            success, result = secure_handle_uploaded_file(file, vid, field_name)
            
            if success:
                # Add the relative path to saved files
                saved_files.append(result)
            else:
                # Add the error message
                errors.append(f"Error with {file.filename}: {result}")
        
        if not saved_files and errors:
            return jsonify({'error': '; '.join(errors)}), 400
        
        # Store the file paths in the database
        try:
            field_value = ViolationFieldValue.query.filter_by(
                violation_id=vid,
                field_definition_id=field_def.id
            ).first()
            
            if field_value:
                # Append to existing files if any
                existing_files = field_value.value.split(',') if field_value.value else []
                # Remove empty strings that might have been in the split
                existing_files = [f for f in existing_files if f.strip()]
                field_value.value = ','.join(existing_files + saved_files)
            else:
                # Create new field value
                db.session.add(ViolationFieldValue(
                    violation_id=vid,
                    field_definition_id=field_def.id,
                    value=','.join(saved_files)
                ))
            
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Database error storing file paths: {str(e)}")
            db.session.rollback()
            return jsonify({'error': f'Database error: {str(e)}'}), 500
        
        # Regenerate the HTML and PDF after adding files
        try:
            # Refresh the violation object from the database to ensure it's bound to the current session
            violation = Violation.query.get(vid)
            html_path, html_content = create_violation_html(violation)
            pdf_path = generate_violation_pdf(violation, html_content)
        except Exception as e:
            current_app.logger.error(f"Error updating violation files after upload: {str(e)}")
        
        return jsonify({
            'message': 'Files uploaded successfully',
            'files': saved_files,
            'warnings': errors if errors else None
        })
    except Exception as e:
        current_app.logger.error(f"Error in file upload: {str(e)}")
        return jsonify({'error': str(e)}), 500

@violation_bp.route('/uploads/<path:filename>')
@login_required
def get_uploaded_file(filename):
    """Securely serve uploaded files with access control"""
    try:
        # Extract violation ID from the path
        path_parts = filename.split('/')
        
        # Check if this is a new-style path (saved_files/uploads/...)
        if 'saved_files' in path_parts:
            # Find the index of 'uploads' in the path
            if 'uploads' in path_parts:
                uploads_index = path_parts.index('uploads')
                # Check if there's a violation folder after 'uploads'
                if len(path_parts) > uploads_index + 2 and path_parts[uploads_index + 2].startswith('violation_'):
                    violation_folder = path_parts[uploads_index + 2]
                    try:
                        violation_id = int(violation_folder.replace('violation_', ''))
                    except ValueError:
                        abort(404)  # Not found
                else:
                    abort(404)  # Not found
            else:
                abort(404)  # Not found
        # Old-style path (direct upload folder)
        elif len(path_parts) >= 1 and path_parts[0].startswith('violation_'):
            try:
                violation_id = int(path_parts[0].replace('violation_', ''))
            except ValueError:
                abort(404)  # Not found
        else:
            abort(404)  # Not found
        
        # Check if the user has permission to access this violation's files
        violation = Violation.query.get_or_404(violation_id)
        if not (current_user.is_admin or violation.created_by == current_user.id):
            abort(403)  # Forbidden
        
        # Determine the base directory
        if 'saved_files' in path_parts:
            # New-style path
            base_dir = os.path.join(current_app.config['BASE_DIR'])
            return send_from_directory(base_dir, filename)
        else:
            # Old-style path (compatibility)
            return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        current_app.logger.error(f"Error serving uploaded file {filename}: {str(e)}")
        abort(500)  # Internal server error

# --- NEW FILE SERVING ROUTE for Evidence ---
@violation_bp.route('/evidence/<int:violation_id>/<filename>')
def get_evidence_file(violation_id, filename):
    """Serve uploaded evidence files securely.
    
    Access requires either:
    1. A logged-in user session.
    2. A valid, non-expired token for the *specific* violation_id passed in the 'token' query parameter.
    """
    is_authorized = False

    # 1. Check for logged-in user
    if current_user.is_authenticated:
        # Optional: Add role-based checks if needed (e.g., only admins?)
        is_authorized = True

    # 2. Check for valid token if not logged in
    if not is_authorized:
        token = request.args.get('token')
        if token:
            # Here we only validate the token exists and is valid, 
            # but don't strictly require it matches the violation_id in the URL
            # IF THE TOKEN ITSELF CONTAINS THE VIOLATION ID.
            # If token is just a general access grant, need different logic.
            # Assuming validate_secure_access_token returns the VIOLATION ID from the token:
            validated_violation_id = validate_secure_access_token(token) 
            if validated_violation_id and validated_violation_id == violation_id:
                is_authorized = True
                current_app.logger.info(f"Access granted via token for violation {violation_id}")
            else:
                 current_app.logger.warning(f"Invalid or mismatched token (token_vid={validated_violation_id}, url_vid={violation_id}) used for evidence {filename}")
        else:
            current_app.logger.warning(f"Attempt to access violation {violation_id} evidence {filename} without login or token.")

    if not is_authorized:
        current_app.logger.warning(f"Unauthorized attempt to access evidence: violation {violation_id}, filename {filename}")
        abort(403) # Forbidden

    # Construct the secure directory path based on the violation ID
    # Ensure this path structure matches where secure_handle_uploaded_file saves files
    # Check secure_handle_uploaded_file: os.path.join(BASE_DIR, 'saved_files', 'uploads', subdir, f'violation_{violation_id}')
    # The subdir used when saving evidence should be consistent here (e.g., 'evidence' or 'fields')
    # Assuming 'fields' as per the previous logic, but VERIFY this.
    directory = os.path.join(
        current_app.config['BASE_DIR'],
        'saved_files',
        'uploads',
        'fields', # <--- VERIFY THIS SUBDIRECTORY MATCHES WHERE EVIDENCE IS SAVED
        f'violation_{violation_id}'
    )

    # Secure the filename just in case
    filename = secure_filename(filename)

    try:
        current_app.logger.info(f"Attempting to serve file: {filename} from directory: {directory}")
        # Check if file exists before attempting to send
        file_path = os.path.join(directory, filename)
        if not os.path.isfile(file_path):
             current_app.logger.error(f"File not found at path: {file_path}")
             abort(404)

        return send_from_directory(directory, filename, as_attachment=False) # Set as_attachment=True to force download
    except FileNotFoundError:
        # This might be redundant if the check above works, but keep for safety
        current_app.logger.error(f"send_from_directory failed: File not found: {filename} in {directory}")
        abort(404) # Not Found
    except Exception as e:
        current_app.logger.error(f"Error serving file {filename} for violation {violation_id}: {e}")
        abort(500) # Internal Server Error

# --- End New Route ---

@violation_bp.route('/api/violations', methods=['GET'])
@login_required
def api_list_violations():
    try:
        MAX_PAGE_SIZE = 100
        # Get query parameters
        try:
            page = int(request.args.get('page', 1))
        except Exception:
            return jsonify({'error': 'Invalid page parameter'}), 400
        try:
            per_page = int(request.args.get('per_page', 10))
        except Exception:
            return jsonify({'error': 'Invalid per_page parameter'}), 400
        date_filter = request.args.get('date_filter', None)
        try:
            limit = request.args.get('limit', None)
            if limit is not None:
                limit = int(limit)
        except Exception:
            return jsonify({'error': 'Invalid limit parameter'}), 400

        # Enforce sensible bounds
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 10
        if per_page > MAX_PAGE_SIZE:
            return jsonify({'error': f'Maximum per_page/limit is {MAX_PAGE_SIZE}'}), 400
        if limit is not None:
            if limit < 1:
                limit = 1
            if limit > MAX_PAGE_SIZE:
                return jsonify({'error': f'Maximum per_page/limit is {MAX_PAGE_SIZE}'}), 400
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
            
            # Add creator email
            try:
                from .models import User
                if row.created_by:
                    creator = User.query.get(row.created_by)
                    if creator:
                        violation['created_by_email'] = creator.email
            except Exception as user_err:
                current_app.logger.warning(f"Error fetching creator for violation {row.id}: {str(user_err)}")
            
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
    
    # Get user who created the violation
    from .models import User
    creator = User.query.get(v.created_by) if v.created_by else None
    creator_email = creator.email if creator else None
    
    # Get all field values for this violation
    field_values = ViolationFieldValue.query.filter_by(violation_id=v.id).all()
    
    # Build a dictionary of field values
    dynamic_fields = {}
    for fv in field_values:
        field_def = fv.field_definition
        dynamic_fields[field_def.name] = fv.value
    
    # Format dates for JSON serialization
    try:
        if v.created_at:
            created_at = v.created_at.isoformat()
        else:
            created_at = None
    except:
        created_at = str(v.created_at) if v.created_at else None
        
    try:
        if v.incident_date:
            incident_date = v.incident_date.isoformat()
        else:
            incident_date = None
    except Exception as err:
        current_app.logger.warning(f"Error formatting incident_date for violation {v.id}: {str(err)}")
        incident_date = str(v.incident_date) if v.incident_date else None
    
    # Format owner/property manager name fields
    owner_property_manager_name = {
        'first': v.owner_property_manager_first_name or '',
        'last': v.owner_property_manager_last_name or ''
    }
    
    # Format tenant name fields
    tenant_name = {
        'first': v.tenant_first_name or '',
        'last': v.tenant_last_name or ''
    }
    
    # Parse attach_evidence if it exists
    attach_evidence = []
    if v.attach_evidence:
        try:
            evidence_files = json.loads(v.attach_evidence)
            if isinstance(evidence_files, list):
                attach_evidence = evidence_files
        except Exception as e:
            current_app.logger.error(f"Error parsing attach_evidence for violation {v.id}: {str(e)}")
            
    result = {
        'id': v.id,
        'public_id': v.public_id if hasattr(v, 'public_id') else None,
        'reference': v.reference,
        'category': v.category,
        'building': v.building,
        'unit_number': v.unit_number,
        'incident_date': incident_date,
        'incident_time': v.incident_time,
        'subject': v.subject,
        'details': v.details,
        'created_at': created_at,
        'created_by': v.created_by,
        'created_by_email': creator_email,
        'dynamic_fields': dynamic_fields,
        'html_path': f"/violations/view/{v.id}" if hasattr(v, 'html_path') and v.html_path else None,
        'pdf_path': f"/violations/pdf/{v.id}" if hasattr(v, 'pdf_path') and v.pdf_path else None,
        'status': v.status,
        
        # Static Violation Fields
        'owner_property_manager_name': owner_property_manager_name,
        'owner_property_manager_email': v.owner_property_manager_email,
        'owner_property_manager_telephone': v.owner_property_manager_telephone,
        'where_did': v.where_did,
        'was_security_or_police_called': v.was_security_or_police_called,
        'fine_levied': v.fine_levied,
        'action_taken': v.action_taken,
        'tenant_name': tenant_name,
        'tenant_email': v.tenant_email,
        'tenant_phone': v.tenant_phone,
        'concierge_shift': v.concierge_shift,
        'noticed_by': v.noticed_by,
        'people_called': v.people_called,
        'actioned_by': v.actioned_by,
        'people_involved': v.people_involved,
        'incident_details': v.incident_details,
        'attach_evidence': attach_evidence
    }
    
    # For frontend compatibility, also map fields to their frontend names
    result['violation_category'] = v.category
    result['unit_no'] = v.unit_number
    result['time'] = v.incident_time
    
    return jsonify(result)

@violation_bp.route('/api/violations/<int:vid>', methods=['PUT'])
@login_required
def api_edit_violation(vid):
    v = Violation.query.get_or_404(vid)
    if not (current_user.is_admin or v.created_by == current_user.id):
        return jsonify({'error': 'Forbidden'}), 403
    
    data = request.json or {}
    old_status = v.status
    
    # Extract owner/property manager name fields if provided in nested format
    if 'owner_property_manager_name' in data and isinstance(data['owner_property_manager_name'], dict):
        data['owner_property_manager_first_name'] = data['owner_property_manager_name'].get('first', '')
        data['owner_property_manager_last_name'] = data['owner_property_manager_name'].get('last', '')
    
    # Extract tenant name fields if provided in nested format
    if 'tenant_name' in data and isinstance(data['tenant_name'], dict):
        data['tenant_first_name'] = data['tenant_name'].get('first', '')
        data['tenant_last_name'] = data['tenant_name'].get('last', '')
        
    # Map frontend field names to model field names
    field_mapping = {
        'violation_category': 'category',
        'unit_no': 'unit_number',
        'time': 'incident_time'
    }
    
    # Process all standard fields, including static violation fields
    static_fields = [
        'category', 'building', 'unit_number', 'incident_date', 'incident_time', 
        'subject', 'details', 'status',
        'owner_property_manager_first_name', 'owner_property_manager_last_name',
        'owner_property_manager_email', 'owner_property_manager_telephone',
        'where_did', 'was_security_or_police_called', 'fine_levied', 'action_taken',
        'tenant_first_name', 'tenant_last_name', 'tenant_email', 'tenant_phone',
        'concierge_shift', 'noticed_by', 'people_called', 'actioned_by', 
        'people_involved', 'incident_details'
    ]
    
    # Update all available fields
    for field in data:
        # Check if field needs mapping
        model_field = field_mapping.get(field, field)
        
        # Only update if field exists in model
        if model_field in static_fields:
            setattr(v, model_field, data[field])
    
    # Process file attachments if present
    attach_evidence = data.get('attach_evidence', [])
    if attach_evidence and isinstance(attach_evidence, list):
        if len(attach_evidence) > 0:
            v.attach_evidence = json.dumps([file.get('name', '') for file in attach_evidence])
        else:
            v.attach_evidence = None
            
    # Process dynamic fields
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
    
    # Log status change if changed
    if old_status != v.status:
        log = ViolationStatusLog(
            violation_id=v.id,
            old_status=old_status,
            new_status=v.status,
            changed_by=current_user.email
        )
        db.session.add(log)
        db.session.commit()
        
    # Regenerate HTML and PDF files after update
    try:
        html_path, html_content = create_violation_html(v)
        pdf_path = generate_violation_pdf(v, html_content)
        
        # Store the updated HTML and PDF paths
        v.html_path = os.path.relpath(html_path, current_app.config['BASE_DIR'])
        v.pdf_path = os.path.relpath(pdf_path, current_app.config['BASE_DIR'])
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error updating violation files after edit: {str(e)}")
        
    return jsonify({
        'success': True,
        'id': v.id,
        'public_id': v.public_id if hasattr(v, 'public_id') else None
    })

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

@violation_bp.route('/api/violations/<int:vid>/replies', methods=['GET'])
@login_required
def api_violation_replies(vid):
    """Get replies for a violation"""
    from .models import ViolationReply
    
    # Check permission
    violation = Violation.query.get_or_404(vid)
    if not (current_user.is_admin or violation.created_by == current_user.id):
        return jsonify({'error': 'Forbidden'}), 403
        
    # Get replies
    replies = ViolationReply.query.filter_by(violation_id=vid).order_by(ViolationReply.created_at).all()
    
    # Format the replies
    formatted_replies = []
    for reply in replies:
        formatted_replies.append({
            'id': reply.id,
            'email': reply.email,
            'response_text': reply.response_text,
            'created_at': reply.created_at.isoformat() if reply.created_at else None,
            'ip_address': reply.ip_address
        })
    
    return jsonify(formatted_replies)

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
        # Refresh the violation object from the database to ensure it's bound to the current session
        violation = Violation.query.get(vid)
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
    
    # Get the violation (refresh from database to ensure session binding)
    reply = ViolationReply.query.get(reply.id)  # Refresh reply object
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
    
    # Generate secure URLs
    secure_urls = send_secure_urls(violation)
    view_url = secure_urls['html_url']
    
    # Prepare email
    subject = f"New Response to Violation {violation.reference}"
    
    # Email body
    body_text = f"""A new response has been added to violation {violation.reference}.

From: {reply.email}
Date: {reply.created_at.strftime('%Y-%m-%d %H:%M:%S')}

Response:
{reply.response_text}

You can view the full details at:
{view_url}

This link is valid for 24 hours and your access will be logged for security purposes.
"""
    
    # Using a regular string instead of f-string to avoid backslash issues
    html_body = """
    <p>A new response has been added to violation {reference}.</p>
    
    <p><strong>From:</strong> {email}<br>
    <strong>Date:</strong> {date}</p>
    
    <p><strong>Response:</strong><br>
    {response_br}</p>
    
    <p>You can view the full details by <a href="{url}">clicking here</a>.</p>
    <p><small>This link is valid for 24 hours and your access will be logged for security purposes.</small></p>
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

@violation_bp.route('/violations/secure/<token>')
def view_secure_violation(token):
    """Public route to securely view a violation with token authentication"""
    # Validate the token and get violation ID
    violation_id = validate_secure_access_token(token)
    if not violation_id:
        current_app.logger.warning(f"Invalid or expired token attempted: {token}")
        abort(403)  # Forbidden
    
    # Get the violation (try with ID first, then with public_id if not found)
    violation = Violation.query.get(violation_id)
    if not violation:
        # If not found by ID, try finding by public_id
        violation = Violation.query.filter_by(public_id=violation_id).first()
        if not violation:
            current_app.logger.warning(f"Violation not found for ID or public_id: {violation_id}")
            abort(404)  # Not found
    
    # Log the access
    log_violation_access(violation.id, token, request)
    
    # Check if an HTML file already exists
    if not violation.html_path:
        try:
            # Generate a new HTML file if it doesn't exist
            html_path, _ = create_violation_html(violation)
            if not html_path:
                abort(500)  # Internal Server Error
        except Exception as e:
            current_app.logger.error(f"Error generating HTML for violation {violation.id}: {str(e)}")
            abort(500)  # Internal Server Error
    else:
        # Get the directory and filename
        html_full_path = os.path.join(current_app.config['BASE_DIR'], violation.html_path)
        if not os.path.exists(html_full_path):
            try:
                # Re-generate if the file doesn't exist at the stored path
                html_path, _ = create_violation_html(violation)
                if not html_path:
                    abort(500)  # Internal Server Error
            except Exception as e:
                current_app.logger.error(f"Error regenerating HTML for violation {violation.id}: {str(e)}")
                abort(500)  # Internal Server Error
    
    # Get the directory and filename from the path
    html_dir = os.path.dirname(os.path.join(current_app.config['BASE_DIR'], violation.html_path))
    html_filename = os.path.basename(violation.html_path)
    
    # Serve the file
    return send_from_directory(html_dir, html_filename)

@violation_bp.route('/violations/secure/<token>/pdf')
def download_secure_violation_pdf(token):
    """Download a violation PDF with token authentication"""
    # Validate the token and get violation ID
    violation_id = validate_secure_access_token(token)
    if not violation_id:
        current_app.logger.warning(f"Invalid or expired token attempted for PDF: {token}")
        abort(403)  # Forbidden
    
    # Get the violation (try with ID first, then with public_id if not found)
    violation = Violation.query.get(violation_id)
    if not violation:
        # If not found by ID, try finding by public_id
        violation = Violation.query.filter_by(public_id=violation_id).first()
        if not violation:
            current_app.logger.warning(f"Violation not found for ID or public_id: {violation_id}")
            abort(404)  # Not found
    
    # Log the access
    log_violation_access(violation.id, token, request)
    
    # Check if a PDF file already exists
    if not violation.pdf_path:
        try:
            # Generate the HTML first if needed
            if not violation.html_path:
                html_path, html_content = create_violation_html(violation)
            else:
                # Read the existing HTML content
                html_full_path = os.path.join(current_app.config['BASE_DIR'], violation.html_path)
                if os.path.exists(html_full_path):
                    with open(html_full_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                else:
                    # Re-generate HTML if file is missing
                    html_path, html_content = create_violation_html(violation)
            
            # Generate the PDF using the HTML content
            pdf_path = generate_violation_pdf(violation, html_content)
            if not pdf_path:
                abort(500)  # Internal Server Error
        except Exception as e:
            current_app.logger.error(f"Error generating PDF for violation {violation.id}: {str(e)}")
            abort(500)  # Internal Server Error
    else:
        # Check if the file exists at the stored path
        pdf_full_path = os.path.join(current_app.config['BASE_DIR'], violation.pdf_path)
        if not os.path.exists(pdf_full_path):
            try:
                # Re-generate if the file doesn't exist
                if not violation.html_path:
                    html_path, html_content = create_violation_html(violation)
                else:
                    # Read the existing HTML content
                    html_full_path = os.path.join(current_app.config['BASE_DIR'], violation.html_path)
                    if os.path.exists(html_full_path):
                        with open(html_full_path, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                    else:
                        # Re-generate HTML if file is missing
                        html_path, html_content = create_violation_html(violation)
                
                # Generate the PDF using the HTML content
                pdf_path = generate_violation_pdf(violation, html_content)
                if not pdf_path:
                    abort(500)  # Internal Server Error
            except Exception as e:
                current_app.logger.error(f"Error regenerating PDF for violation {violation.id}: {str(e)}")
                abort(500)  # Internal Server Error
    
    # Get the directory and filename from the path
    pdf_dir = os.path.dirname(os.path.join(current_app.config['BASE_DIR'], violation.pdf_path))
    pdf_filename = os.path.basename(violation.pdf_path)
    
    # Serve the file
    return send_from_directory(
        pdf_dir,
        pdf_filename,
        as_attachment=True,
        download_name=f"violation_{violation.reference}.pdf"
    )

def send_secure_urls(violation):
    """Generate secure URLs for a violation
    
    Args:
        violation: The violation object
        
    Returns:
        dict: Dictionary with secure URLs
    """
    # Generate token for this violation
    token = generate_secure_access_token(violation.id)
    
    # Get base URL
    base_url = current_app.config.get('BASE_URL', f"http://{request.host}")
    
    # Create secure URLs
    html_url = f"{base_url}/violations/secure/{token}"
    pdf_url = f"{base_url}/violations/secure/{token}/pdf"
    
    return {
        'html_url': html_url,
        'pdf_url': pdf_url,
        'token': token
    }

@violation_bp.route('/api/violations/<int:vid>/status_log', methods=['GET'])
@login_required
def api_violation_status_log(vid):
    logs = ViolationStatusLog.query.filter_by(violation_id=vid).order_by(ViolationStatusLog.timestamp).all()
    return jsonify([
        {
            'old_status': log.old_status,
            'new_status': log.new_status,
            'changed_by': log.changed_by,
            'timestamp': log.timestamp.isoformat()
        } for log in logs
    ])

@violation_bp.route('/api/violations/public/<uuid:public_id>', methods=['GET'])
@login_required
def api_violation_detail_public(public_id):
    """Fetch violation details using the public UUID."""
    # Convert UUID object to string for filtering
    public_id_str = str(public_id)
    v = Violation.query.filter_by(public_id=public_id_str).first_or_404()
    # Reuse the existing detail logic by calling the ID-based endpoint internally
    # Or duplicate the logic here for clarity
    if not (current_user.is_admin or v.created_by == current_user.id):
        return jsonify({'error': 'Forbidden'}), 403
    from .models import User
    creator = User.query.get(v.created_by) if v.created_by else None
    creator_email = creator.email if creator else None
    field_values = ViolationFieldValue.query.filter_by(violation_id=v.id).all()
    dynamic_fields = {}
    for fv in field_values:
        field_def = fv.field_definition
        if field_def: # Check if field_def exists
           dynamic_fields[field_def.name] = fv.value
    try:
        created_at = v.created_at.isoformat() if v.created_at else None
    except: created_at = str(v.created_at) if v.created_at else None
    try:
        incident_date = v.incident_date.isoformat() if v.incident_date else None
    except: incident_date = str(v.incident_date) if v.incident_date else None
    owner_property_manager_name = {'first': v.owner_property_manager_first_name or '', 'last': v.owner_property_manager_last_name or ''}
    tenant_name = {'first': v.tenant_first_name or '', 'last': v.tenant_last_name or ''}
    attach_evidence = []
    if v.attach_evidence:
        try:
            evidence_files = json.loads(v.attach_evidence)
            if isinstance(evidence_files, list):
                attach_evidence = evidence_files
        except Exception as e:
            current_app.logger.error(f"Error parsing attach_evidence for violation {v.id}: {str(e)}")
    result = {
        'id': v.id,
        'public_id': v.public_id,
        'reference': v.reference,
        'category': v.category,
        'building': v.building,
        'unit_number': v.unit_number,
        'incident_date': incident_date,
        'incident_time': v.incident_time,
        'subject': v.subject,
        'details': v.details,
        'created_at': created_at,
        'created_by': v.created_by,
        'created_by_email': creator_email,
        'dynamic_fields': dynamic_fields, # Keep for potential legacy data
        'html_path': f"/violations/view/{v.id}" if hasattr(v, 'html_path') and v.html_path else None,
        'pdf_path': f"/violations/pdf/{v.id}" if hasattr(v, 'pdf_path') and v.pdf_path else None,
        'status': v.status,
        'owner_property_manager_name': owner_property_manager_name,
        'owner_property_manager_email': v.owner_property_manager_email,
        'owner_property_manager_telephone': v.owner_property_manager_telephone,
        'where_did': v.where_did,
        'was_security_or_police_called': v.was_security_or_police_called,
        'fine_levied': v.fine_levied,
        'action_taken': v.action_taken,
        'tenant_name': tenant_name,
        'tenant_email': v.tenant_email,
        'tenant_phone': v.tenant_phone,
        'concierge_shift': v.concierge_shift,
        'noticed_by': v.noticed_by,
        'people_called': v.people_called,
        'actioned_by': v.actioned_by,
        'people_involved': v.people_involved,
        'incident_details': v.incident_details,
        'attach_evidence': attach_evidence
    }
    result['violation_category'] = v.category
    result['unit_no'] = v.unit_number
    result['time'] = v.incident_time
    return jsonify(result)
