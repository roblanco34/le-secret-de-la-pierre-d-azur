from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

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