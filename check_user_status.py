#!/usr/bin/env python
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    # Print all users with their approval status
    print("Users and their status:")
    for user in User.query.all():
        print(f"Email: {user.email}, Admin: {user.is_admin}, Approved: {getattr(user, 'approved', 'N/A')}")
    
    # Find and approve the test user
    test_user = User.query.filter_by(email='test@example.com').first()
    if test_user:
        # Check if 'approved' attribute exists
        if hasattr(test_user, 'approved'):
            test_user.approved = True
            db.session.commit()
            print(f"\nApproved user: {test_user.email}")
        else:
            print(f"\nUser {test_user.email} doesn't have an 'approved' field.")
            
            # Check if there's a 'status' field instead
            if hasattr(test_user, 'status'):
                test_user.status = 'approved'
                db.session.commit()
                print(f"Updated status to 'approved' for {test_user.email}")
            else:
                print(f"User {test_user.email} doesn't have a 'status' field either.")
                # Let's inspect all attributes of the user object
                print("\nUser attributes:")
                for attr in dir(test_user):
                    if not attr.startswith('_') and not callable(getattr(test_user, attr)):
                        print(f"{attr}: {getattr(test_user, attr)}")
    else:
        print("Test user not found") 