from flask import Blueprint, request, jsonify, current_app, send_from_directory, render_template, abort, send_file
from flask_login import login_required, current_user
from .models import Violation, FieldDefinition, ViolationFieldValue
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
    active_only = request.args.get('active') == 'true'
    if active_only:
        fields = get_cached_fields('active')
    else:
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
        'validation': f.validation
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
        'validation': f.validation
    } for f in fields])

@violation_bp.route('/api/violations', methods=['POST'])
@login_required
def api_create_violation():
    data = request.json or {}
    
    # Generate a reference number if not provided
    if not data.get('reference'):
        now = datetime.datetime.now()
        reference = f"VIO-{now.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        data['reference'] = reference
    
    # Create new violation
    violation = Violation(
        reference=data.get('reference', ''),
        category=data.get('category', ''),
        building=data.get('building', ''),
        unit_number=data.get('unit_number', ''),
        incident_date=data.get('incident_date'),
        subject=data.get('subject', ''),
        details=data.get('details', ''),
        created_by=current_user.id
    )
    
    db.session.add(violation)
    db.session.flush()  # Get the violation ID before commit
    
    # Process dynamic fields
    dynamic_fields = data.get('dynamic_fields', {})
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
    
    db.session.commit()
    
    # Generate HTML and PDF for the violation
    try:
        # Get all field definitions for HTML generation, using cache
        field_defs = get_cached_fields('all')
        
        # Create the HTML file
        html_path, html_content = create_violation_html(violation, field_defs)
        
        # Generate the PDF file
        pdf_path = generate_violation_pdf(violation, html_content)
        
        # Send email notification
        send_violation_notification(violation, html_path)
        
        # Store the HTML and PDF paths in the database
        violation.html_path = os.path.relpath(html_path, current_app.config['BASE_DIR'])
        violation.pdf_path = os.path.relpath(pdf_path, current_app.config['BASE_DIR'])
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error generating violation files: {str(e)}")
    
    return jsonify({
        'id': violation.id,
        'message': 'Violation created successfully'
    }), 201

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
    
    # If the file doesn't exist, create it
    if not os.path.exists(pdf_path):
        try:
            pdf_path = generate_violation_pdf(violation)
        except Exception as e:
            current_app.logger.error(f"Error generating PDF: {str(e)}")
            abort(500, description="Could not generate PDF")
    
    # Serve the PDF file
    return send_file(
        pdf_path, 
        download_name=f"violation_{violation.reference}.pdf",
        as_attachment=True,
        mimetype='application/pdf'
    )

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
        limit = request.args.get('limit', type=int)
        
        # Build a SQL query to avoid ORM issues with missing columns
        if current_user.is_admin:
            sql = "SELECT id, reference, category, building, unit_number, created_at, created_by, subject, details, html_path, pdf_path FROM violations ORDER BY created_at DESC"
        else:
            sql = "SELECT id, reference, category, building, unit_number, created_at, created_by, subject, details, html_path, pdf_path FROM violations WHERE created_by = :user_id ORDER BY created_at DESC"
        
        if limit:
            sql += f" LIMIT {limit}"
            
        # Execute query directly
        result = db.session.execute(text(sql), {"user_id": current_user.id})
        
        # Process results
        violations = []
        for row in result:
            violation = {
                'id': row.id,
                'reference': row.reference or '',
                'category': row.category or '',
                'building': row.building or '',
                'unit_number': row.unit_number or '',
                'created_at': row.created_at.isoformat() if row.created_at else None,
                'created_by': row.created_by,
                'subject': row.subject or '',
                'details': row.details or '',
                'html_path': f"/violations/view/{row.id}" if row.html_path else None,
                'pdf_path': f"/violations/pdf/{row.id}" if row.pdf_path else None,
                'dynamic_fields': {}  # We'll skip dynamic fields for now
            }
            violations.append(violation)
            
        return jsonify(violations)
    except Exception as e:
        current_app.logger.error(f"Error fetching violations: {str(e)}")
        return jsonify([])  # Return empty list instead of error to avoid breaking the UI

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
    result = {
        'id': v.id,
        'reference': v.reference,
        'category': v.category,
        'building': v.building,
        'unit_number': v.unit_number,
        'incident_date': v.incident_date.isoformat() if v.incident_date else None,
        'subject': v.subject,
        'details': v.details,
        'created_at': v.created_at.isoformat() if hasattr(v, 'created_at') and v.created_at else None,
        'created_by': v.created_by,
        'dynamic_fields': dynamic_fields,
        'html_path': f"/violations/view/{v.id}" if hasattr(v, 'html_path') else None,
        'pdf_path': f"/violations/pdf/{v.id}" if hasattr(v, 'pdf_path') else None
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
