from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

def add_admin_user(email, password):
    app = create_app()
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"User {email} already exists.")
            if not existing_user.is_admin:
                existing_user.promote_to_admin()
                print(f"User {email} has been promoted to admin.")
            return

        # Create new admin user
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            is_admin=True,
            is_active=True
        )
        db.session.add(user)
        db.session.commit()
        print(f"Admin user {email} has been created successfully.")

if __name__ == "__main__":
    add_admin_user("dcook@spectrum4.ca", "password") 