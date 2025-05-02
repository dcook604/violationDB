#!/usr/bin/env python3
"""
Script to reset the admin user's password to a known value
"""
from app import create_app, db
from app.models import User

def reset_admin_password():
    app = create_app()
    with app.app_context():
        # Find the admin user
        admin = User.query.filter_by(email='admin@example.com').first()
        
        if admin:
            print(f"Found admin user: {admin.email}")
            print(f"Current status: is_admin={admin.is_admin}, is_active={admin.is_active}")
            
            # Reset password
            new_password = 'admin123'
            admin.set_password(new_password)
            
            # Ensure admin privileges
            admin.is_admin = True
            admin.is_active = True
            admin.failed_login_attempts = 0
            admin.account_locked_until = None
            
            db.session.commit()
            
            print(f"Password reset to '{new_password}' for admin user")
            print("User account is now active and has admin privileges")
            print("Failed login attempts have been reset")
        else:
            print("Admin user not found. Creating a new admin user...")
            admin = User(
                email='admin@example.com',
                is_admin=True,
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Created new admin user with password 'admin123'")

if __name__ == "__main__":
    reset_admin_password() 