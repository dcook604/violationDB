from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from .models import UnitProfile, Violation # Import necessary models
from . import db
from .auth_routes import admin_required_api # Assuming admin decorator exists
from sqlalchemy import func # For aggregation
from datetime import datetime, timedelta

unit_bp = Blueprint('units', __name__)

# --- Unit Profile CRUD ---

@unit_bp.route('/api/units', methods=['GET'])
@login_required
def list_units():
    """List basic unit info (unit number, owner name). Add search/pagination later."""
    try:
        # Basic query for now, add search/pagination as needed
        units = UnitProfile.query.order_by(UnitProfile.unit_number).all()
        return jsonify([{
            'id': u.id,
            'unit_number': u.unit_number,
            'owner_last_name': u.owner_last_name
        } for u in units])
    except Exception as e:
        current_app.logger.error(f"Error listing units: {str(e)}")
        return jsonify({'error': 'Failed to retrieve units'}), 500

@unit_bp.route('/api/units', methods=['POST'])
@login_required
@admin_required_api # Protect this route
def create_unit():
    """Create a new unit profile."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required = ['unit_number', 'owner_first_name', 'owner_last_name', 'owner_email', 'owner_telephone']
    if not all(field in data and data[field] for field in required):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if unit number already exists
    if UnitProfile.query.filter_by(unit_number=data['unit_number']).first():
        return jsonify({'error': 'Unit number already exists'}), 409 # Conflict

    try:
        new_unit = UnitProfile(
            unit_number=data['unit_number'],
            strata_lot_number=data.get('strata_lot_number'),
            owner_first_name=data['owner_first_name'],
            owner_last_name=data['owner_last_name'],
            owner_email=data['owner_email'],
            owner_telephone=data['owner_telephone'],
            owner_mailing_address=data.get('owner_mailing_address'),
            parking_stall_numbers=data.get('parking_stall_numbers'),
            bike_storage_numbers=data.get('bike_storage_numbers'),
            has_dog=data.get('has_dog', False),
            has_cat=data.get('has_cat', False),
            is_rented=data.get('is_rented', False),
            tenant_first_name=data.get('tenant_first_name') if data.get('is_rented') else None,
            tenant_last_name=data.get('tenant_last_name') if data.get('is_rented') else None,
            tenant_email=data.get('tenant_email') if data.get('is_rented') else None,
            tenant_telephone=data.get('tenant_telephone') if data.get('is_rented') else None,
            updated_by=current_user.id
        )
        db.session.add(new_unit)
        db.session.commit()
        # TODO: Add to audit log
        current_app.logger.info(f"Unit profile created: {new_unit.unit_number} by {current_user.email}")
        return jsonify(new_unit.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating unit profile: {str(e)}")
        return jsonify({'error': 'Failed to create unit profile'}), 500

@unit_bp.route('/api/units/<unit_number>', methods=['GET'])
@login_required
def get_unit_detail(unit_number):
    """Get full details for a specific unit."""
    unit = UnitProfile.query.filter_by(unit_number=unit_number).first_or_404()
    # Add permission check if regular users should only see their own?
    return jsonify(unit.to_dict())

@unit_bp.route('/api/units/<unit_number>', methods=['PUT'])
@login_required
@admin_required_api # Or add more granular permissions
def update_unit(unit_number):
    """Update an existing unit profile."""
    unit = UnitProfile.query.filter_by(unit_number=unit_number).first_or_404()
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Update fields provided in the request
    # Consider adding validation here too
    try:
        for key, value in data.items():
            if hasattr(unit, key) and key not in ['id', 'unit_number', 'created_at', 'updated_at', 'updated_by']: # Prevent updating protected fields
                setattr(unit, key, value)
        
        # Ensure tenant info is cleared if not rented
        if not data.get('is_rented', unit.is_rented):
            unit.tenant_first_name = None
            unit.tenant_last_name = None
            unit.tenant_email = None
            unit.tenant_telephone = None
            
        unit.updated_by = current_user.id
        db.session.commit()
        # TODO: Add to audit log (capture diff)
        current_app.logger.info(f"Unit profile updated: {unit.unit_number} by {current_user.email}")
        return jsonify(unit.to_dict())
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating unit profile {unit.unit_number}: {str(e)}")
        return jsonify({'error': 'Failed to update unit profile'}), 500

@unit_bp.route('/api/units/<unit_number>', methods=['DELETE'])
@login_required
@admin_required_api # Protect this route
def delete_unit(unit_number):
    """Delete a unit profile."""
    unit = UnitProfile.query.filter_by(unit_number=unit_number).first_or_404()
    try:
        # Consider implications: What happens to related violations?
        # Option 1: Just delete profile (violations remain associated via unit_number string)
        # Option 2: Check for violations and prevent deletion / reassign / anonymize?
        # For now, just delete the profile.
        db.session.delete(unit)
        db.session.commit()
        # TODO: Add to audit log
        current_app.logger.info(f"Unit profile deleted: {unit.unit_number} by {current_user.email}")
        return jsonify({'message': 'Unit profile deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting unit profile {unit.unit_number}: {str(e)}")
        return jsonify({'error': 'Failed to delete unit profile'}), 500

# --- Violation Summary Endpoint ---

@unit_bp.route('/api/units/<unit_number>/violation_summary')
@login_required
def get_violation_summary(unit_number):
    """Get violation summary for a unit."""
    # Verify the unit exists
    unit = UnitProfile.query.filter_by(unit_number=unit_number).first_or_404()
    
    try:
        # 1. Violation counts per year (last 5 years)
        counts = {}
        today = datetime.utcnow()
        for i in range(5):
            year = today.year - i
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, 12, 31, 23, 59, 59)
            count = db.session.query(func.count(Violation.id)).filter(
                Violation.unit_number == unit_number,
                Violation.created_at >= start_date,
                Violation.created_at <= end_date
            ).scalar()
            counts[str(year)] = count
        
        # 2. Outstanding violations (example: status is not 'Closed')
        # Adjust status names as needed
        closed_statuses = ['Closed-No Fine Issued', 'Closed-Fines Issued', 'Reject']
        outstanding = Violation.query.filter(
            Violation.unit_number == unit_number,
            Violation.status.notin_(closed_statuses)
        ).order_by(Violation.created_at.desc()).all()
        
        outstanding_list = [{
            'id': v.id,
            'public_id': v.public_id,
            'reference': v.reference,
            'category': v.category,
            'created_at': v.created_at.isoformat() if v.created_at else None,
            'status': v.status
        } for v in outstanding]
        
        # 3. Fines levied (simple sum for now, adjust if needed)
        # This assumes `fine_levied` stores a numeric value or easily parseable string like '$100.00'
        total_fine = 0
        # Query needed here based on how fines are stored. If stored in the violation field:
        # Example: Query violations for the unit and parse/sum the `fine_levied` field
        # This part needs refinement based on actual fine storage/logic
        
        return jsonify({
            'violation_counts_last_5_years': counts,
            'outstanding_violations': outstanding_list,
            'total_fines_levied': str(total_fine) # Format as needed
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting violation summary for unit {unit_number}: {str(e)}")
        return jsonify({'error': 'Failed to retrieve violation summary'}), 500 