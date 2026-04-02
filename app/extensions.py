from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# Page renvoyée si un @login_required n'est pas satisfait
login_manager.login_view = "auth.login"
login_manager.login_message = "Connecte-toi pour accéder à cette page."