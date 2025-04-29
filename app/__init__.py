import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

# Configure logging to save errors to flask_error.log
logging.basicConfig(
    filename='flask_error.log',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    from .config import Config
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    mail.init_app(app)

    from . import routes, models, auth_routes
    from .violation_routes import violation_bp
    app.register_blueprint(routes.bp)
    app.register_blueprint(auth_routes.auth_bp)
    app.register_blueprint(violation_bp)

    return app
