# Le secret de la pierre d'azur
Chasse au trésor du secret de la pierre d'azur, accessible depuis l'URL [http://pierre-azur.sc2dero1876.universe.wf/](http://pierre-azur.sc2dero1876.universe.wf/).

## Architecture du projet

### Proposition GPT
```
le-secret-de-la-pierre-d-azur/
│
├── pierre_azur/
│   ├── __init__.py
│   ├── routes.py
│   ├── game.py
│   ├── models.py
│   ├── utils.py
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── game.html
│   │   ├── waiting.html
│   │   └── video.html
│   │
│   └── static/
│       ├── style.css
│       └── images/
│
├── database.db
├── config.py
├── passenger_wsgi.py
├── requirements.txt
└── run.py   (dev uniquement)
```

### Proposition Claude

```
treasure_hunt/
│
├── app/
│   ├── __init__.py             # create_app()
│   ├── extensions.py           # db, login_manager
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # User (id, name, password, role)
│   │   ├── enigme.py           # Enigme (id, manche, enigme, name, instruction, response)
│   │   └── progress.py         # Progress (id, user_id, enigme_id, attempt, start, end, time)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py             # /login, /logout
│   │   ├── game.py             # /index, /enigme/<id>
│   │   └── admin.py            # /admin (plus tard)
│   ├── services/
│   │   ├── auth_service.py     # hash/vérif password
│   │   ├── game_service.py     # logique progression, vérif réponse, normalisation
│   │   └── admin_service.py    # déblocage des manches (plus tard)
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── index.html
│   │   └── enigme.html
│   └── static/
│
├── migrations/
├── tests/
├── config.py
├── .env
├── requirements.txt
└── run.py
```

```
# User
id        | Integer  | PK
name      | String   | unique, not null
password  | String   | hashed
role      | String   | "player" | "admin"

# Enigme
id          | Integer  | PK — ordre global dans l'histoire (1→15)
manche      | Integer  | 1, 2 ou 3
enigme      | Integer  | 1→5 au sein de la manche
name        | String
instruction | Text
video_url   | String   | (à ajouter)
response    | String   | stockée normalisée

# Progress
id          | Integer  | PK
user_id     | FK → User
enigme_id   | FK → Enigme
attempt     | Integer  | default=0, incrémenté à chaque essai
start       | DateTime | 1er affichage de l'énigme
end         | DateTime | nullable, rempli à la bonne réponse
time        | Integer  | secondes (end - start), nullable
```

#### Flux de jeu — schéma
```
Admin débloque manche N
        │
        ▼
Joueur arrive sur /index
→ voit les manches débloquées
→ voit sa progression (énigmes réussies / en cours)
        │
        ▼
Clique sur une énigme → /enigme/<id>
→ si Progress inexistant : création avec start=now()
→ affiche vidéo + instruction + input réponse
        │
        ▼
Soumet une réponse
→ attempt + 1
→ normalisation (minuscules, sans accents)
→ comparaison avec enigme.response
        │
   ┌────┴────┐
Bonne       Mauvaise
réponse     réponse
   │            │
end=now()   message d'erreur
time=calculé    retour formulaire
redirect /index
```
