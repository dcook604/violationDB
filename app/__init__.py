import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import os

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

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
