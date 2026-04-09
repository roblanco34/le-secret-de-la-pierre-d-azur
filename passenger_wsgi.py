import sys
import os

# Indique à Passenger où se trouve ton projet
CHEMIN = os.path.dirname(__file__)
sys.path.insert(0, CHEMIN)

# Charge les variables d'environnement depuis .env
from dotenv import load_dotenv
load_dotenv(os.path.join(CHEMIN, ".env"))

# Importe et expose l'app Flask sous le nom 'application'
from app import create_app
application = create_app("production")