# Le secret de la pierre d'azur
Chasse au trésor du secret de la pierre d'azur, accessible depuis l'URL [http://pierre-azur.sc2dero1876.universe.wf/](http://pierre-azur.sc2dero1876.universe.wf/).

## Architecture du projet

*A valider*
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