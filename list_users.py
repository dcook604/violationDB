#!/usr/bin/env python
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    users = User.query.all()
    print('Available users:')
    for user in users:
        print(f'Email: {user.email}, Admin: {user.is_admin}') 