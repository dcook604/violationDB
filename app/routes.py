from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .models import Violation
from . import db
from app.forms import ViolationForm
import os
from datetime import datetime

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
from app.forms import ViolationForm
import os
from datetime import datetime

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)






# --- Registration ---
from .forms import RegisterForm

@bp.route('/register', methods=['GET', 'POST'])
def register():
    from werkzeug.security import generate_password_hash
    from .models import User
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('main.register'))
        user = User(email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)



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
