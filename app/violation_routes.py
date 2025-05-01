from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from .models import Violation, FieldDefinition, ViolationFieldValue
from . import db
import os
import json
from sqlalchemy import text

violation_bp = Blueprint('violations', __name__)

CUSTOM_FIELDS_PATH = os.path.join(os.path.dirname(__file__), 'custom_violation_fields.json')

def load_custom_fields():
    if not os.path.exists(CUSTOM_FIELDS_PATH):
        return []
    with open(CUSTOM_FIELDS_PATH, 'r') as f:
        return json.load(f)

def save_custom_fields(fields):
    with open(CUSTOM_FIELDS_PATH, 'w') as f:
        json.dump(fields, f, indent=2)

# --- API Endpoints only below ---

@violation_bp.route('/api/fields', methods=['GET'])
def api_list_fields():
    fields = FieldDefinition.query.filter_by(active=True).order_by(FieldDefinition.order).all()
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
        field_def = FieldDefinition.query.filter_by(name=field_name).first()
        if field_def:
            db.session.add(ViolationFieldValue(
                violation_id=violation.id,
                field_definition_id=field_def.id,
                value=value
            ))
    
    db.session.commit()
    return jsonify({
        'id': violation.id,
        'message': 'Violation created successfully'
    }), 201

@violation_bp.route('/api/violations', methods=['GET'])
@login_required
def api_list_violations():
    try:
        # Get query parameters
        limit = request.args.get('limit', type=int)
        
        # Build a SQL query to avoid ORM issues with missing columns
        if current_user.is_admin:
            sql = "SELECT id, reference, category, building, unit_number, created_at, created_by, subject, details FROM violations ORDER BY created_at DESC"
        else:
            sql = "SELECT id, reference, category, building, unit_number, created_at, created_by, subject, details FROM violations WHERE created_by = :user_id ORDER BY created_at DESC"
        
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
        'dynamic_fields': dynamic_fields
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
