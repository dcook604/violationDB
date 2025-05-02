#!/usr/bin/env python
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash
import datetime

app = create_app()
with app.app_context():
    # Check if test user already exists
    test_user = User.query.filter_by(email='test@example.com').first()
    
    if test_user:
        print(f"Test user already exists: {test_user.email}, Admin: {test_user.is_admin}")
        # Update password
        test_user.password_hash = generate_password_hash('test123')
        db.session.commit()
        print("Password reset to 'test123'")
    else:
        # Create new test user
        test_user = User(
            email='test@example.com',
            password_hash=generate_password_hash('test123'),
            role='user',
            is_admin=True,
            created_at=datetime.datetime.now()
        )
        db.session.add(test_user)
        db.session.commit()
        print(f"Created new test user: {test_user.email}, Admin: {test_user.is_admin}")
    
    # List all users
    print("\nAll users in the database:")
    for user in User.query.all():
        print(f"Email: {user.email}, Admin: {user.is_admin}") 