#!/usr/bin/env python
from app import create_app, db
from app.models import User
import json

app = create_app()
with app.app_context():
    # Get admin user
    admin = User.query.filter_by(email='admin@example.com').first()
    
    if admin:
        print(f"\nAdmin User Information:")
        print(f"Email: {admin.email}")
        print(f"Role: {admin.role}")
        print(f"is_admin (Boolean): {admin.is_admin}")
        print(f"is_active: {admin.is_active}")
        
        # This will print all non-callable attributes that don't start with _
        print("\nAll user attributes:")
        attrs = {}
        for attr in dir(admin):
            if not attr.startswith('_') and not callable(getattr(admin, attr)):
                value = getattr(admin, attr)
                if not isinstance(value, type):
                    attrs[attr] = str(value)
        
        for key, value in sorted(attrs.items()):
            print(f"{key}: {value}")
    else:
        print("Admin user not found") 