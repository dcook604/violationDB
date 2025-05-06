from flask import Blueprint, jsonify, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .models import Violation
from . import db
from app.forms import ViolationForm
import os
from datetime import datetime
from flask_jwt_extended import get_jwt, get_jwt_identity
from app.jwt_auth import jwt_required_api

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/dashboard')
@jwt_required_api
def dashboard():
    return jsonify({
        'user': {
            'id': get_jwt_identity(),
            'email': get_jwt().get('email'),
            'role': 'admin' if get_jwt().get('is_admin') else 'user'
        }
    })

# --- Registration ---
from .forms import RegisterForm

@bp.route('/register')
def register():
    return jsonify({'redirect': True, 'location': 'http://localhost:3001/register'}), 200

# --- Password Reset (simple version) ---
@bp.route('/reset-password')
def reset_password():
    return jsonify({'redirect': True, 'location': 'http://localhost:3001/reset-password'}), 200
