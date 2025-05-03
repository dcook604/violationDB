from app import create_app, db
from app.models import User

def update_admin():
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email='admin@example.com').first()
        if user:
            user.first_name = 'Daniel'
            user.last_name = 'Cook'
            db.session.commit()
            print(f'User {user.email} updated with first_name={user.first_name}, last_name={user.last_name}')
        else:
            print('User admin@example.com not found')

if __name__ == '__main__':
    update_admin() 