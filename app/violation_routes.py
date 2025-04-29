from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from .models import Violation
from .forms import ViolationForm
from . import db
from .utils import save_uploaded_file, generate_pdf_from_html, send_email

import json
import os
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

@violation_bp.route('/admin/custom-fields', methods=['GET', 'POST'])
@login_required
def admin_custom_fields():
    if not current_user.is_admin:
        flash('Admin access required.', 'danger')
        return redirect(url_for('violations.list_violations'))
    custom_fields = load_custom_fields()
    if request.method == 'POST':
        if 'delete' in request.args:
            # Delete a field
            field_name = request.args['delete']
            custom_fields = [f for f in custom_fields if f['name'] != field_name]
            save_custom_fields(custom_fields)
            flash(f'Field {field_name} deleted.', 'success')
            return redirect(url_for('violations.admin_custom_fields'))
        else:
            # Add a new field
            name = request.form.get('field_name', '').strip()
            label = request.form.get('field_label', '').strip() or name
            ftype = request.form.get('field_type', 'text')
            if name and name not in [f['name'] for f in custom_fields]:
                custom_fields.append({'name': name, 'label': label, 'type': ftype})
                save_custom_fields(custom_fields)
                flash(f'Field {label} added.', 'success')
            else:
                flash('Field name required and must be unique.', 'danger')
            return redirect(url_for('violations.admin_custom_fields'))
    return render_template('admin_custom_fields.html', custom_fields=custom_fields)

@violation_bp.route('/violations')
@login_required
def list_violations():
    violations = Violation.query.order_by(Violation.created_at.desc()).all()
    return render_template('violations.html', violations=violations)

CATEGORIES = ['Noise', 'Parking', 'Garbage', 'Pets', 'Other']
MANAGERS = ['Site Manager', 'Building Manager', 'Security', 'Council']
UNITS = ['#1705', '#1605', '#1606', '#1607', '#1608']

@violation_bp.route('/violations/new', methods=['GET', 'POST'])
@login_required
def new_violation():
    form = ViolationForm()
    from datetime import datetime
    today_date = datetime.utcnow().strftime('%Y-%m-%d')
    custom_fields = load_custom_fields()
    extra_fields = {}
    if request.method == 'POST':
        for field in custom_fields:
            val = request.form.get(f'custom_{field["name"]}', '').strip()
            extra_fields[field['name']] = val
    if form.validate_on_submit():
        import random
        unique_ref = f"V-{datetime.utcnow().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        v = Violation(
            reference=unique_ref,
            category=form.category.data,
            building=form.building.data,
            unit_number=form.unit_number.data,
            incident_date=form.incident_date.data,
            subject=form.subject.data,
            details=form.details.data,
            extra_fields=extra_fields,
            created_by=current_user.id
        )
        db.session.add(v)
        db.session.commit()
        # Only do PDF/email if not testing
        if not current_app.config.get('TESTING'):
            try:
                # PDF/email logic would go here
                pass
            except Exception:
                pass
        flash('Violation submitted!', 'success')
        return redirect(url_for('violations.list_violations'))
    # Always pass context for both GET and POST (validation fail)
    return render_template('new_violation.html', form=form, categories=CATEGORIES, managers=MANAGERS, units=UNITS, today_date=today_date, custom_fields=custom_fields)


@violation_bp.route('/violations/<int:vid>')
@login_required
def view_violation(vid):
    violation = Violation.query.get_or_404(vid)
    return render_template('view_violation.html', v=violation)

@violation_bp.route('/violations/<int:vid>/edit', methods=['GET', 'POST'])
@login_required
def edit_violation(vid):
    violation = Violation.query.get_or_404(vid)
    form = ViolationForm(obj=violation)
    if not (current_user.is_admin or violation.created_by == current_user.id):
        flash('You do not have permission to edit this violation.', 'danger')
        return redirect(url_for('violations.list_violations'))
    if form.validate_on_submit():
        violation.category = form.category.data
        violation.building = form.building.data
        violation.unit_number = form.unit_number.data
        violation.incident_date = form.incident_date.data
        violation.subject = form.subject.data
        violation.details = form.details.data
        db.session.commit()
        flash('Violation updated.', 'success')
        return redirect(url_for('violations.list_violations'))
    return render_template('edit_violation.html', form=form, v=violation)

@violation_bp.route('/violations/<int:vid>/delete', methods=['POST'])
@login_required
def delete_violation(vid):
    violation = Violation.query.get_or_404(vid)
    if not (current_user.is_admin or violation.created_by == current_user.id):
        flash('You do not have permission to delete this violation.', 'danger')
        return redirect(url_for('violations.list_violations'))
    db.session.delete(violation)
    db.session.commit()
    flash('Violation deleted.', 'success')
    return redirect(url_for('violations.list_violations'))
