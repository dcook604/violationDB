from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .models import User
from . import db
from .auth_routes import send_activation_email

admin_bp = Blueprint('admin', __name__)

# Removed old user management routes as they are now handled in user_routes.py
