#!/usr/bin/env python
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

app = create_app()
with app.app_context():
    # Find admin user
    admin_user = User.query.filter_by(email='admin@example.com').first()
    
    if admin_user:
        print(f"Admin user exists: {admin_user.email}")
        print(f"Admin status: {admin_user.is_admin}")
        print(f"Active status: {admin_user.is_active}")
        print(f"User role: {admin_user.role}")
        
        # Set consistent password and make sure account is properly configured
        new_password = 'admin123'
        admin_user.password_hash = generate_password_hash(new_password)
        admin_user.is_active = True
        admin_user.role = 'admin'
        
        # Clear any temporary password
        admin_user.temp_password = None
        admin_user.temp_password_expiry = None
        
        # Commit changes
        db.session.commit()
        
        # Verify login would work by checking the password directly
        if check_password_hash(admin_user.password_hash, new_password):
            print(f"\nPassword verification successful for {admin_user.email}")
            print(f"You should be able to login with:\nEmail: {admin_user.email}\nPassword: {new_password}")
        else:
            print(f"\nPassword verification FAILED for {admin_user.email}")
    else:
        print("Admin user not found. Creating a new admin user...")
        
        # Create new admin user
        new_admin = User(
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True,
            is_active=True,
            role='admin',
            created_at=datetime.datetime.now()
        )
        db.session.add(new_admin)
        db.session.commit()
        
        print(f"Created new admin user: admin@example.com with password: admin123")
        
    # Verify the login logic directly
    print("\nSimulating login process...")
    user = User.query.filter_by(email='admin@example.com').first()
    if user and check_password_hash(user.password_hash, 'admin123'):
        if user.is_active:
            print("Login would succeed! User is active and password matches.")
        else:
            print("Login would fail! User is not active.")
    else:
        print("Login would fail! Invalid credentials.") 