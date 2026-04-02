import os
from flask import Flask
from .extensions import db, migrate, login_manager
from config import config
from .models import User, Enigme, Progress

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "default")

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialisation des extensions avec l'app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Enregistrement des blueprints
    from .routes import auth_bp, game_bp  # 👈 depuis routes.py directement
    app.register_blueprint(auth_bp)
    app.register_blueprint(game_bp)

    with app.app_context():
        from . import models  # 👈 indispensable pour Flask-Migrate

    return app