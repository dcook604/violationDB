from flask import Blueprint, jsonify, current_app
from flask_login import login_required, current_user
from .models import Violation, User, ViolationFieldValue, FieldDefinition
from sqlalchemy import text
from . import db

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    try:
        # Get total violations count
        if current_user.is_admin:
            # Admin sees all violations
            query = text("SELECT COUNT(*) FROM violations")
            result = db.session.execute(query)
        else:
            # Regular users only see their violations
            query = text("SELECT COUNT(*) FROM violations WHERE created_by = :user_id")
            result = db.session.execute(query, {"user_id": current_user.id})
            
        total_count = result.scalar() or 0
        
        # Get all violations to check their Status field
        if current_user.is_admin:
            violations = Violation.query.all()
        else:
            violations = Violation.query.filter_by(created_by=current_user.id).all()
        
        # Count active violations (those with specific Status values in dynamic fields)
        active_violations = 0
        resolved_violations = 0
        
        # Find the field definition for Status
        status_field = FieldDefinition.query.filter_by(name='Status').first()
        
        for violation in violations:
            # Default to active if no Status field exists
            is_active = True
            
            if status_field:
                # Try to get the Status field value for this violation
                field_value = ViolationFieldValue.query.filter_by(
                    violation_id=violation.id,
                    field_definition_id=status_field.id
                ).first()
                
                if field_value and field_value.value:
                    # Check if status is one of the active statuses
                    active_statuses = ['Open', 'Pending Owner Response', 'Pending Council Response']
                    is_active = field_value.value in active_statuses
            
            # Count the violation as active or resolved
            if is_active:
                active_violations += 1
            else:
                resolved_violations += 1
        
        return jsonify({
            'totalViolations': total_count,
            'activeViolations': active_violations,
            'resolvedViolations': resolved_violations
        })
    except Exception as e:
        # Log the error
        current_app.logger.error(f"Error in get_stats: {str(e)}")
        
        # Return default values in case of error
        return jsonify({
            'totalViolations': 0,
            'activeViolations': 0,
            'resolvedViolations': 0
        }) 