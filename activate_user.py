#!/usr/bin/env python
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    # Find and activate both users
    for email in ['test@example.com', 'admin@example.com']:
        user = User.query.filter_by(email=email).first()
        if user:
            # Set account to active
            user.is_active = True
            print(f"Activating user: {user.email}")
            db.session.commit()
    
    # Print all users with their updated status
    print("\nUpdated user statuses:")
    for user in User.query.all():
        print(f"Email: {user.email}, Admin: {user.is_admin}, Active: {user.is_active}") 