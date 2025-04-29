from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from .models import Violation
from .forms import ViolationForm
from . import db
from .utils import save_uploaded_file, generate_pdf_from_html, send_email

violation_bp = Blueprint('violations', __name__)

@violation_bp.route('/violations')
@login_required
def list_violations():
    violations = Violation.query.order_by(Violation.created_at.desc()).all()
    return render_template('violations.html', violations=violations)

@violation_bp.route('/violations/new', methods=['GET', 'POST'])
@login_required
def new_violation():
    form = ViolationForm()
    if form.validate_on_submit():
        # Save violation and files, generate PDF, send email (logic omitted for brevity)
        flash('Violation submitted!', 'success')
        return redirect(url_for('violations.list_violations'))
    return render_template('new_violation.html', form=form)

@violation_bp.route('/violations/<int:vid>')
@login_required
def view_violation(vid):
    violation = Violation.query.get_or_404(vid)
    return render_template('view_violation.html', v=violation)

@violation_bp.route('/violations/<int:vid>/edit', methods=['GET', 'POST'])
@login_required
def edit_violation(vid):
    violation = Violation.query.get_or_404(vid)
    if not (current_user.is_admin or violation.created_by == current_user.id):
        flash('You do not have permission to edit this violation.', 'danger')
        return redirect(url_for('violations.list_violations'))
    form = ViolationForm(obj=violation)
    if form.validate_on_submit():
        # Update violation fields
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
