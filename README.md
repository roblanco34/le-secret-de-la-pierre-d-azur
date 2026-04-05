# Le secret de la pierre d'azur

## Présentation
Chasse au trésor **Le secret de la Pierre d'Azur**, accessible depuis l'URL [http://pierre-azur.sc2dero1876.universe.wf/](http://pierre-azur.sc2dero1876.universe.wf/).

Cette application possède 2 profils :
- `player` : permet de participer aux manches et énigmes, et d'envoyer des réponses.
- `admin` : permet de créer ou réinitialiser des utilisateurs, voir l'avancement des players et débloquer les manches.

## Documentation
### Architecture du projet

```
le-secret-de-la-pierre-d-azur/
│
├── app/
│   ├── __init__.py          # create_app() — Application Factory
│   ├── extensions.py        # db, migrate, login_manager, admin_required
│   ├── models.py            # User, Enigme, Progress, Config
│   ├── routes.py            # auth_bp, game_bp, admin_bp
│   ├── services.py          # logique métier (auth, jeu, admin)
│   ├── static/
│   │   └── style.css
│   └── templates/
│       ├── base.html
│       ├── login.html
│       ├── index.html
│       ├── enigme.html
│       └── admin.html
│
├── migrations/              # versionning schéma (Flask-Migrate)
├── instance/
│   └── database.db          # SQLite (jamais commité)
├── passenger_wsgi.py        # point d'entrée production (o2switch)
├── config.py                # DevelopmentConfig / ProductionConfig
├── requirements.txt
├── .env                     # secrets (jamais commité)
└── run.py                   # point d'entrée développement
```

### Les modèles

```
┌─────────────────────┐        ┌──────────────────────────┐
│        User         │        │          Enigme           │
├─────────────────────┤        ├──────────────────────────┤
│ id          Integer │        │ id          Integer       │
│ name        String  │        │ manche      Integer 1-3  │
│ password    String  │        │ enigme      Integer 1-5  │
│ role        String  │        │ name        String       │
│                     │        │ instruction Text         │
│ is_admin  @property │        │ video_url   String       │
└──────────┬──────────┘        │ response    String (norm)│
           │                   └────────────┬─────────────┘
           │ 1                              │ 1
           │                               │
           └──────────────┬────────────────┘
                          │ N
               ┌──────────┴──────────┐
               │       Progress      │
               ├─────────────────────┤
               │ id          Integer │
               │ user_id     FK      │
               │ enigme_id   FK      │
               │ attempt     Integer │
               │ start       DateTime│
               │ end         DateTime│  ← null si non résolue
               │ time        Integer │  ← secondes (end-start)
               │                    │
               │ is_solved @property│
               │ solve()   @method  │
               └────────────────────┘

┌─────────────────────┐
│       Config        │  ← table clé/valeur
├─────────────────────┤
│ key         String  │  ex: "manches_debloquees" → "1,2"
│ value       String  │
└─────────────────────┘
```

### Flux de jeu

```
[ Admin ]
                            │
                    débloque manche N
                            │
                            ▼
[ Joueur ] ──── /login ──► /index
                            │
                  ┌─────────┴──────────┐
                  │  Carte de la quête │
                  │  Manche 1          │
                  │  ✓ Énigme 1        │  ← résolue
                  │  › Énigme 2        │  ← accessible
                  │  ✕ Énigme 3        │  ← verrouillée
                  │  Manche 2  🔒      │  ← non débloquée
                  └─────────┬──────────┘
                            │ clique "Commencer / Continuer"
                            ▼
                      /enigme/<id>
                            │
                   Progress existant ?
                      │           │
                     Non         Oui
                      │           │
               start = now()     (on reprend)
                      └─────┬─────┘
                            │
                    affiche vidéo
                    + instruction
                    + input réponse
                            │
                        soumet
                            │
                   attempt += 1
                   normalize(réponse)
                            │
                  ┌─────────┴──────────┐
                 Bonne              Mauvaise
                réponse             réponse
                  │                     │
          end = now()            flash "Mauvaise réponse"
          time = end - start     retour formulaire
                  │
          toutes les énigmes
          de la manche résolues ?
                  │
         ┌────────┴────────┐
        Non               Oui
         │                 │
      /index            /index
                  (attend manche suivante
                   ou fin de la chasse)
```

## A faire
- Ajouter vidéo d'introduction du jeu (model Config)
- AJOUTER LE NB DE TENTATIVE POUR L'ADMIN
- Ajout bouton Refresh
- Ajouter la possibilité de supprimer des joueurs (à côté de réinitialiser)
- Un compte administrateur ne peut pas être joueur
- Ajouter l'attribut 'indice' dans enigme + l'administrateur peut l'afficher/activer et le rendre visible dans enigme (per user) [clic depuis la progression des joueurs?]
- Texte : NOM DU CHASSEUR -> NOM DE L'EQUIPE