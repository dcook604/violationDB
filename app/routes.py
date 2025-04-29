from flask import Blueprint, render_template
from flask_login import login_required, current_user

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .models import Violation
from . import db
import os
from datetime import datetime

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@bp.route('/violations/new', methods=['GET', 'POST'])
@login_required
def new_violation():
    categories = [
        'Noise', 'Parking', 'Garbage', 'Pets', 'Other'
    ]
    managers = [
        'Site Manager', 'Building Manager', 'Security', 'Council'
    ]
    units = ['#1705', '#1605', '#1606', '#1607', '#1608']
    if request.method == 'POST':
        form = request.form
        entry_date = form.get('entry_date')
        category = form.get('category')
        building = form.get('building')
        incident_units = request.form.getlist('incident_units')
        incident_area = form.get('incident_area')
        report_to = form.get('report_to')
        concierge_shift = form.get('concierge_shift')
        incident_time = form.get('incident_time')
        people_involved = form.get('people_involved')
        noticed_by = form.get('noticed_by')
        people_called = form.get('people_called')
        subject = form.get('subject')
        details = form.get('details')
        initial_action = form.get('initial_action')
        resolution = form.get('resolution')

        # Handle file uploads
        photo_files = request.files.getlist('photos')
        pdf_files = request.files.getlist('pdfs')
        photo_paths = []
        pdf_paths = []
        uploads_dir = os.path.join(current_app.root_path, 'uploads')
        photos_dir = os.path.join(uploads_dir, 'photos')
        pdfs_dir = os.path.join(uploads_dir, 'pdfs')
        os.makedirs(photos_dir, exist_ok=True)
        os.makedirs(pdfs_dir, exist_ok=True)
        for file in photo_files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                path = os.path.join('uploads/photos', filename)
                file.save(os.path.join(current_app.root_path, path))
                photo_paths.append(path)
        for file in pdf_files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                path = os.path.join('uploads/pdfs', filename)
                file.save(os.path.join(current_app.root_path, path))
                pdf_paths.append(path)
        # Get resident email if provided (for demo, use noticed_by as resident_email)
        resident_email = form.get('resident_email') or noticed_by or 'resident@example.com'
        violation = Violation(
            created_by=current_user.id,
            category=category,
            building=building,
            unit_number=','.join(incident_units),
            incident_area=incident_area,
            report_to=report_to,
            concierge_shift=concierge_shift,
            incident_date=datetime.strptime(entry_date, '%Y-%m-%d').date() if entry_date else None,
            incident_time=datetime.strptime(incident_time, '%H:%M').time() if incident_time else None,
            people_involved=people_involved,
            noticed_by=noticed_by,
            people_called=people_called,
            subject=subject,
            details=details,
            initial_action=initial_action,
            resolution=resolution,
            photo_paths=','.join(photo_paths),
            pdf_paths=','.join(pdf_paths),
            resident_email=resident_email
        )
        db.session.add(violation)
        db.session.commit()

        # PDF Generation
        from flask import render_template as flask_render_template
        from weasyprint import HTML
        pdf_template = flask_render_template('pdf_violation.html', v=violation)
        pdf_dir = os.path.join(current_app.root_path, 'uploads/pdfs')
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_filename = f"violation_{violation.id}.pdf"
        pdf_path = os.path.join(pdf_dir, pdf_filename)
        HTML(string=pdf_template).write_pdf(pdf_path)
        violation.pdf_letter_path = f"uploads/pdfs/{pdf_filename}"
        db.session.commit()

        # Email Sending
        from flask_mail import Message
        from . import mail
        msg = Message(
            subject=f"Violation Report: {violation.subject or violation.category}",
            sender=current_app.config.get('MAIL_USERNAME'),
            recipients=[violation.resident_email],
            cc=["welcome@ascent.com", "council@spectrum4.ca"]
        )
        msg.body = f"Dear Resident,\n\nPlease find attached the violation report.\n\nRegards,\nStrata Council"
        with open(pdf_path, 'rb') as fp:
            msg.attach(pdf_filename, 'application/pdf', fp.read())
        try:
            mail.send(msg)
        except Exception as e:
            flash(f"Warning: Could not send email: {e}", "warning")

        flash('Violation submitted successfully and emailed!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template(
        'new_violation.html',
        categories=categories,
        managers=managers,
        units=units,
        today_date=datetime.utcnow().strftime('%Y-%m-%d')
    )

@bp.route('/violations', methods=['GET'])
@login_required
def view_violations():
    query = Violation.query
    unit_number = request.args.get('unit_number', '').strip()
    category = request.args.get('category', '').strip()
    incident_date = request.args.get('incident_date', '').strip()
    if unit_number:
        query = query.filter(Violation.unit_number.like(f"%{unit_number}%"))
    if category:
        query = query.filter(Violation.category == category)
    if incident_date:
        try:
            date_obj = datetime.strptime(incident_date, '%Y-%m-%d').date()
            query = query.filter(Violation.incident_date == date_obj)
        except Exception:
            pass
    violations = query.order_by(Violation.created_at.desc()).all()
    categories = ['Noise', 'Parking', 'Garbage', 'Pets', 'Other']
    return render_template('violations.html', violations=violations, categories=categories)

@bp.route('/violations/<int:vid>/edit', methods=['GET', 'POST'])
@login_required
def edit_violation(vid):
    violation = Violation.query.get_or_404(vid)
    if not (current_user.is_admin or violation.created_by == current_user.id):
        flash('You do not have permission to edit this violation.', 'danger')
        return redirect(url_for('main.view_violations'))
    if request.method == 'POST':
        violation.details = request.form.get('details', violation.details)
        violation.initial_action = request.form.get('initial_action', violation.initial_action)
        violation.resolution = request.form.get('resolution', violation.resolution)
        db.session.commit()
        flash('Violation updated.', 'success')
        return redirect(url_for('main.view_violations'))
    return render_template('edit_violation.html', v=violation)

@bp.route('/violations/<int:vid>/delete', methods=['POST'])
@login_required
def delete_violation(vid):
    violation = Violation.query.get_or_404(vid)
    if not (current_user.is_admin or violation.created_by == current_user.id):
        flash('You do not have permission to delete this violation.', 'danger')
        return redirect(url_for('main.view_violations'))
    db.session.delete(violation)
    db.session.commit()
    flash('Violation deleted.', 'success')
    return redirect(url_for('main.view_violations'))

@bp.route('/violations/<int:vid>', methods=['GET'])
@login_required
def view_violation(vid):
    violation = Violation.query.get_or_404(vid)
    return render_template('view_violation.html', v=violation)

# --- User Management (Admin) ---
@bp.route('/admin/users')
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('Admins only.', 'danger')
        return redirect(url_for('main.dashboard'))
    from .models import User
    users = User.query.order_by(User.email).all()
    return render_template('manage_users.html', users=users)

@bp.route('/admin/users/<int:uid>/promote', methods=['POST'])
@login_required
def promote_user(uid):
    if not current_user.is_admin:
        flash('Admins only.', 'danger')
        return redirect(url_for('main.dashboard'))
    from .models import User
    user = User.query.get_or_404(uid)
    user.is_admin = True
    db.session.commit()
    flash(f'User {user.email} promoted to admin.', 'success')
    return redirect(url_for('main.manage_users'))

@bp.route('/admin/users/<int:uid>/demote', methods=['POST'])
@login_required
def demote_user(uid):
    if not current_user.is_admin:
        flash('Admins only.', 'danger')
        return redirect(url_for('main.dashboard'))
    from .models import User
    user = User.query.get_or_404(uid)
    user.is_admin = False
    db.session.commit()
    flash(f'User {user.email} demoted from admin.', 'success')
    return redirect(url_for('main.manage_users'))

# --- Registration ---
@bp.route('/register', methods=['GET', 'POST'])
def register():
    from werkzeug.security import generate_password_hash
    from .models import User
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('main.register'))
        user = User(email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

# --- Password Reset (simple version) ---
@bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    from werkzeug.security import generate_password_hash
    from .models import User
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Email not found.', 'danger')
            return redirect(url_for('main.reset_password'))
        new_password = request.form['new_password']
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash('Password reset successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html')
