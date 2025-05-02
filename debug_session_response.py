#!/usr/bin/env python
from app import create_app, db
from app.models import User
from flask import session, jsonify
from flask_login import login_user, current_user
import json

app = create_app()
with app.app_context():
    # Get the admin user
    admin = User.query.filter_by(email='admin@example.com').first()
    
    if admin:
        print(f"\nAdmin user exists:")
        print(f"Email: {admin.email}")
        print(f"Role: {admin.role}")
        print(f"Is Admin: {admin.is_admin}")
        
        # Create a test request context
        with app.test_request_context():
            # Login the user
            login_user(admin)
            
            # Check current_user
            print("\nCurrent user after login:")
            print(f"Authenticated: {current_user.is_authenticated}")
            print(f"Is Admin: {current_user.is_admin}")
            
            # Simulate session check response
            print("\nSimulated session check response:")
            if current_user.is_authenticated:
                user_data = {
                    'id': current_user.id,
                    'email': current_user.email,
                    'role': 'admin' if current_user.is_admin else 'user'
                }
                response = {'user': user_data}
                print(json.dumps(response, indent=2))
            else:
                response = {'user': None}
                print(json.dumps(response, indent=2))
    else:
        print("Admin user not found") 