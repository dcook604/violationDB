from flask import Blueprint, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from .models import User, FieldDefinition
from . import db

admin_bp = Blueprint('admin', __name__)

# Removed old user management routes as they are now handled in user_routes.py

@admin_bp.route('/api/fields', methods=['GET'])
@login_required
def list_fields():
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    fields = FieldDefinition.query.order_by(FieldDefinition.order).all()
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

@admin_bp.route('/api/fields', methods=['POST'])
@login_required
def create_field():
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    data = request.get_json()
    field = FieldDefinition(
        name=data['name'],
        label=data.get('label', data['name']),
        type=data['type'],
        required=data.get('required', False),
        options=data.get('options'),
        order=data.get('order', 0),
        active=data.get('active', True),
        validation=data.get('validation')
    )
    db.session.add(field)
    db.session.commit()
    return jsonify({'message': 'Field created', 'id': field.id}), 201

@admin_bp.route('/api/fields/<int:fid>', methods=['PUT'])
@login_required
def update_field(fid):
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    field = FieldDefinition.query.get_or_404(fid)
    data = request.get_json()
    field.label = data.get('label', field.label)
    field.type = data.get('type', field.type)
    field.required = data.get('required', field.required)
    field.options = data.get('options', field.options)
    field.order = data.get('order', field.order)
    field.active = data.get('active', field.active)
    field.validation = data.get('validation', field.validation)
    db.session.commit()
    return jsonify({'message': 'Field updated'})

@admin_bp.route('/api/fields/<int:fid>', methods=['DELETE'])
@login_required
def delete_field(fid):
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    field = FieldDefinition.query.get_or_404(fid)
    db.session.delete(field)
    db.session.commit()
    return jsonify({'message': 'Field deleted'})

@admin_bp.route('/api/fields/<int:fid>/toggle', methods=['POST'])
@login_required
def toggle_field(fid):
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    field = FieldDefinition.query.get_or_404(fid)
    field.active = not field.active
    db.session.commit()
    return jsonify({'message': 'Field toggled', 'active': field.active})

@admin_bp.route('/api/fields/reorder', methods=['POST'])
@login_required
def reorder_fields():
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    data = request.get_json()
    for idx, fid in enumerate(data['order']):
        field = FieldDefinition.query.get(fid)
        if field:
            field.order = idx
    db.session.commit()
    return jsonify({'message': 'Fields reordered'})
