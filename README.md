# Le Secret de la Pierre d'Azur

> Chasse au trésor en ligne — Bretagne (35)

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-lightgrey)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57)
![Licence](https://img.shields.io/badge/Licence-CC%20BY--NC--ND%204.0-green)

---

## Présentation

Application web de chasse au trésor jouée en équipe, optimisée pour smartphone.  
Une seule chasse organisée entre amis, composée de **3 manches de 5 énigmes** chacune.

Les manches sont débloquées manuellement par un administrateur. Au sein d'une manche
débloquée, chaque joueur progresse à son rythme dans l'ordre des énigmes.

---

## Fonctionnalités

- Authentification par nom / mot de passe
- Progression individuelle par énigme (tentatives illimitées)
- Vidéo + instruction par énigme
- Indices activables par l'admin pour un joueur donné
- Tableau de bord admin en temps réel (progression, tentatives, indices)
- Gestion des joueurs (création, réinitialisation, suppression)
- Déblocage des manches à la main

---

## Stack technique

| Composant | Technologie |
|---|---|
| Framework | Flask 3.x |
| ORM | Flask-SQLAlchemy |
| Base de données | SQLite |
| Migrations | Flask-Migrate (Alembic) |
| Authentification | Flask-Login |
| Serveur de prod | Passenger (o2switch) |
| Front | Jinja2 + CSS custom (mobile-first) |

---

## Architecture

```
le-secret-de-la-pierre-d-azur/
├── app/
│   ├── __init__.py          # create_app() — Application 
│   ├── extensions.py        # db, migrate, login_manager, admin_required
│   ├── models.py            # User, Enigme, Progress, Attempt, Config
│   ├── routes.py            # auth_bp, game_bp, admin_bp
│   ├── services.py          # logique métier
│   ├── static/
│   │   └── style.css
│   └── templates/
│       ├── base.html
│       ├── login.html
│       ├── index.html
│       ├── enigme.html
│       └── admin.html
├── migrations/
├── instance/
│   └── database.db          # jamais commité
├── enigmes.json             # contenu des énigmes
├── passenger_wsgi.py        # point d'entrée production
├── config.py
├── requirements.txt
├── .env                     # jamais commité
└── run.py                   # point d'entrée développement
```

---

## Installation locale

### Prérequis

- Python 3.12+
- pip

### Étapes

```bash
# 1. Cloner le repo
git clone https://github.com/toi/le-secret-de-la-pierre-d-azur.git
cd le-secret-de-la-pierre-d-azur

# 2. Créer et activer le virtualenv
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Mac/Linux

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Créer le fichier .env
echo "SECRET_KEY=change_moi\nFLASK_ENV=development" > .env

# 5. Initialiser la base de données
flask db upgrade

# 6. Créer un compte admin
flask shell
>>> from app.extensions import db
>>> from app.models import User
>>> from app.services import hash_password
>>> admin = User(name="admin", password=hash_password("ton_mdp"), role="admin")
>>> db.session.add(admin)
>>> db.session.commit()

# 8. Lancer le serveur
python run.py
```

L'application est accessible sur `http://127.0.0.1:5000`.

---

## Gestion des énigmes

Les énigmes sont gérés directement depuis la table `enigmes` de la base de données.

Pour le moment, il est nécessaire de récupérer la `database.db` générée afin de mettre à jour les énigmes et de la remplacer.

---

## Déploiement sur o2switch

```bash
# 1. Cloner le repo sur le serveur
cd /home/user
git clone https://github.com/toi/le-secret-de-la-pierre-d-azur.git

# 2. Créer le .env
nano le-secret-de-la-pierre-d-azur/.env

# 3. Activer le virtualenv (commande fournie par cPanel Setup Python App)
source /home/user/virtualenv/le-secret-de-la-pierre-d-azur/3.12/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Initialiser la DB
flask db upgrade

# 6. Redémarrer depuis cPanel Setup Python App → Restart
```

Pour mettre à jour après un push :

```bash
cd /home/user/le-secret-de-la-pierre-d-azur
git pull
# Puis Restart depuis cPanel
```

---

## Variables d'environnement

| Variable | Description | Exemple |
|---|---|---|
| `SECRET_KEY` | Clé de chiffrement des sessions | `token_hex(32)` |
| `FLASK_ENV` | Environnement (`development` / `production`) | `production` |

---

## Fichiers à ne jamais commiter

```
.env
instance/database.db
passenger_wsgi.py   # spécifique au serveur
```

---

## Licence

Ce projet est publié sous licence **Creative Commons BY-NC-ND 4.0**.  
Voir le fichier [LICENSE](LICENSE) pour les détails.