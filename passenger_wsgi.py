import sys
import os

CHEMIN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CHEMIN)

from dotenv import load_dotenv
load_dotenv(os.path.join(CHEMIN, ".env"))

from app import create_app
application = create_app("production")