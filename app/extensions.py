from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from functools import wraps
from flask import abort, redirect, url_for
from flask_login import current_user

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# Page renvoyée si un @login_required n'est pas satisfait
login_manager.login_view = "auth.login"
login_manager.login_message = "Connecte-toi pour accéder à cette page."

@login_manager.user_loader
def load_user(user_id):
    from .models import User          # import ici pour éviter le import circulaire
    return User.query.get(int(user_id))


def admin_required(f):
    """Décorateur qui réserve une route aux admins."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated

def player_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.is_admin:
            return redirect(url_for("admin.index"))
        return f(*args, **kwargs)
    return decorated