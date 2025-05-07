from flask import Blueprint, jsonify, current_app
from flask_login import login_required, current_user
from .models import Violation, User, ViolationFieldValue, FieldDefinition
from sqlalchemy import text, func
from . import db
from datetime import datetime, timedelta
from .jwt_auth import jwt_required_api
from flask_jwt_extended import get_jwt, get_jwt_identity
from . import limiter

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/api/stats', methods=['GET'])
@limiter.limit("200 per hour")  # Increased rate limit from default 50 per hour
@jwt_required_api
def get_stats():
    try:
        claims = get_jwt()
        is_admin = claims.get('is_admin')
        user_id = get_jwt_identity()
        # Get violations from the last year
        one_year_ago = datetime.utcnow() - timedelta(days=365)

        # Get total violations count from the last year
        if is_admin:
            # Admin sees all violations
            last_year_count = Violation.query.filter(
                Violation.created_at >= one_year_ago
            ).count()
        else:
            # Regular users only see their violations
            last_year_count = Violation.query.filter(
                Violation.created_by == user_id,
                Violation.created_at >= one_year_ago
            ).count()
        
        # Get count of all violations (used for active/resolved)
        if is_admin:
            violations = Violation.query.all()
        else:
            violations = Violation.query.filter_by(created_by=user_id).all()
        
        # Get repeat offenders (units with multiple violations)
        if is_admin:
            repeat_offenders_query = db.session.query(
                Violation.unit_number, func.count(Violation.id).label('count')
            ).group_by(Violation.unit_number).having(func.count(Violation.id) > 1)
        else:
            repeat_offenders_query = db.session.query(
                Violation.unit_number, func.count(Violation.id).label('count')
            ).filter(Violation.created_by == user_id
            ).group_by(Violation.unit_number).having(func.count(Violation.id) > 1)
        
        repeat_offenders_count = repeat_offenders_query.count()
        
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
            'totalViolationsLastYear': last_year_count,
            'repeatOffenders': repeat_offenders_count,
            'activeViolations': active_violations,
            'resolvedViolations': resolved_violations
        })
    except Exception as e:
        import traceback
        current_app.logger.error(f"Error in get_stats: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        # Return default values in case of error
        return jsonify({
            'totalViolationsLastYear': 0,
            'repeatOffenders': 0,
            'activeViolations': 0,
            'resolvedViolations': 0
        }) 