from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"


class Config:
    """Flask Configuration Settings"""
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")  # Load from env
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///site.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


def create_app():
    """Application Factory"""
    app = Flask(__name__)
    app.config.from_object(Config)  # Load configuration

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Import and register blueprints
    from app.auth.routes import auth
    app.register_blueprint(auth)

    return app
