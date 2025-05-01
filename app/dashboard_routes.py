from flask import Blueprint, jsonify, current_app
from flask_login import login_required, current_user
from .models import Violation, User
from sqlalchemy import text
from . import db

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    try:
        # Use a simple direct SQL count query to avoid ORM issues
        if current_user.is_admin:
            # Admin sees all violations
            query = text("SELECT COUNT(*) FROM violations")
        else:
            # Regular users only see their violations
            query = text("SELECT COUNT(*) FROM violations WHERE created_by = :user_id")
            
        result = db.session.execute(query, {"user_id": current_user.id})
        count = result.scalar() or 0
        
        # For now, assume all violations are active
        return jsonify({
            'totalViolations': count,
            'activeViolations': count,
            'resolvedViolations': 0
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