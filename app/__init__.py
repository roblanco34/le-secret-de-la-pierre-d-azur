import os
from flask import Flask
from .extensions import db, migrate, login_manager
from config import config
from .models import User, Enigme, Progress
from datetime import timezone, timedelta


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

    @app.template_filter("heure_locale")
    def heure_locale_filter(dt):
        if dt is None:
            return "—"
        # UTC+2 en été (CEST), UTC+1 en hiver (CET)
        # Pour la Bretagne, ajuste selon la saison de ta chasse
        local = dt.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=2)))
        return local.strftime('%H:%M:%S')
    
    #     #Affichage du temps en minutes et secondes
    # @app.template_filter("minutes")
    # def minutes_filter(secondes):
    #     if secondes is None:
    #         return "—"
    #     m = secondes // 60
    #     s = secondes % 60
    #     return f"{m}m{s:02d}s"

    return app

    @app.context_processor
    def inject_user_state():
        """Injecte l'état du joueur dans tous les templates."""
        from flask_login import current_user
        from .models import Progress
        from .services import get_manches_debloquees

        if not current_user.is_authenticated or current_user.is_admin:
            return {"current_user_state": None}

        progresses = Progress.query.filter_by(user_id=current_user.id).all()
        return {
            "current_user_state": {
                "enigmes_resolues": [p.enigme_id for p in progresses if p.is_solved],
                "indices_actifs":   [p.enigme_id for p in progresses if p.indice_active],
                "manches":          get_manches_debloquees()
            }
        }

