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
        from .routes import auth_bp, game_bp, admin_bp   # 👈
        app.register_blueprint(admin_bp)  

    #Affichage du temps en minutes
    @app.template_filter("minutes")
    def minutes_filter(secondes):
        if secondes is None:
            return "—"
        m = secondes // 60
        return f"{m}min"
    
    #     #Affichage du temps en minutes et secondes
    # @app.template_filter("minutes")
    # def minutes_filter(secondes):
    #     if secondes is None:
    #         return "—"
    #     m = secondes // 60
    #     s = secondes % 60
    #     return f"{m}m{s:02d}s"

    return app

