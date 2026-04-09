import unicodedata
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db
from .models import User, Enigme, Progress, Attempt, Config

# ── Normalisation ──────────────────────────────────────────────────────────────

def normalize(text):
    """Minuscules + suppression des accents."""
    text = text.strip().lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text


# ── Auth ───────────────────────────────────────────────────────────────────────

def hash_password(password):
    return generate_password_hash(password)

def verify_password(user, password):
    return check_password_hash(user.password, password)

def get_user_by_name(name):
    return User.query.filter_by(name=name).first()


# ── Manches ────────────────────────────────────────────────────────────────────

def get_manches_debloquees():
    """Lit les manches débloquées depuis la table Config."""
    valeur = Config.get("manches_debloquees", default="")
    if not valeur:
        return []
    return [int(m) for m in valeur.split(",") if m.strip().isdigit()]

def set_manches_debloquees(liste_manches):
    """Sauvegarde la liste des manches débloquées. Ex: [1, 2]"""
    Config.set("manches_debloquees", ",".join(str(m) for m in liste_manches))

def get_enigmes_par_manche(manche):
    """Retourne les énigmes d'une manche, triées par numéro."""
    return Enigme.query.filter_by(manche=manche).order_by(Enigme.enigme).all()

def get_intro_video_url():
    return Config.get("intro_video_url", default="")


# ── Progression ────────────────────────────────────────────────────────────────

def get_enigme_courante(user, manche):
    """
    Retourne la prochaine énigme à faire dans une manche.
    Retourne None si toutes résolues.
    """
    enigmes = get_enigmes_par_manche(manche)
    for enigme in enigmes:
        progress = Progress.query.filter_by(
            user_id=user.id,
            enigme_id=enigme.id
        ).first()
        if not progress or not progress.is_solved:
            return enigme
    return None

def is_enigme_accessible(user, enigme):
    """
    Une énigme est accessible si toutes les énigmes
    précédentes de la même manche sont résolues.
    """
    if enigme.enigme == 1:
        return True

    precedente = Enigme.query.filter_by(
        manche=enigme.manche,
        enigme=enigme.enigme - 1
    ).first()

    if not precedente:
        return False

    progress = Progress.query.filter_by(
        user_id=user.id,
        enigme_id=precedente.id
    ).first()

    return progress is not None and progress.is_solved

def get_or_create_progress(user, enigme):
    """
    Récupère le Progress existant ou en crée un nouveau.
    Enregistre start à la première visite.
    """
    progress = Progress.query.filter_by(
        user_id=user.id,
        enigme_id=enigme.id
    ).first()

    if not progress:
        progress = Progress(
            user_id=user.id,
            enigme_id=enigme.id,
            start=datetime.utcnow()
        )
        db.session.add(progress)
        db.session.commit()

    return progress

def get_progression_user(user):
    """
    Retourne toutes les manches avec le statut de chaque énigme.
    {
        1: {
            "debloquee": True,
            "enigmes": [
                {
                    "enigme": <Enigme>,
                    "progress": <Progress|None>,
                    "accessible": True|False
                },
                ...
            ]
        },
        ...
    }
    """
    manches_dispo = get_manches_debloquees()
    result = {}

    for manche in [1, 2, 3]:
        debloquee = manche in manches_dispo
        enigmes   = get_enigmes_par_manche(manche)
        items     = []

        for enigme in enigmes:
            progress = Progress.query.filter_by(
                user_id=user.id,
                enigme_id=enigme.id
            ).first()

            accessible = debloquee and is_enigme_accessible(user, enigme)

            items.append({
                "enigme":     enigme,
                "progress":   progress,
                "accessible": accessible
            })

        result[manche] = {
            "debloquee": debloquee,
            "enigmes":   items
        }

    return result


# ── Vérification de réponse ────────────────────────────────────────────────────

def verifier_reponse(user, enigme, reponse_user):
    """
    Incrémente attempt, enregistre la tentative brute,
    compare la réponse normalisée.
    Retourne (progress, is_correct).
    """
    progress = get_or_create_progress(user, enigme)
    progress.attempt += 1

    attempt = Attempt(
        progress_id=progress.id,
        valeur=reponse_user.strip()
    )
    db.session.add(attempt)

    is_correct = normalize(reponse_user) == enigme.response

    if is_correct and not progress.is_solved:
        progress.solve()

    db.session.commit()
    return progress, is_correct


# ── Admin ──────────────────────────────────────────────────────────────────────

def get_tous_les_joueurs():
    """Retourne tous les users avec le rôle player."""
    return User.query.filter_by(role="player").order_by(User.name).all()

def get_vue_globale():
    """
    Retourne la progression de tous les joueurs sur toutes les énigmes.
    [
        {
            "user":                   <User>,
            "total_resolues":         int,
            "total_enigmes":          int,
            "progression":            { manche: { enigme: <Progress|None> } },
            "progression_enigmes":    { manche: { enigme: <Enigme> } },
            "progression_attempts":   { manche: { enigme: [<Attempt>] } }
        },
        ...
    ]
    """
    joueurs       = get_tous_les_joueurs()
    toutes_enigmes = Enigme.query.order_by(Enigme.manche, Enigme.enigme).all()
    total         = len(toutes_enigmes)
    result        = []

    for joueur in joueurs:
        progression          = {}
        progression_enigmes  = {}
        progression_attempts = {}
        resolues             = 0

        for enigme in toutes_enigmes:
            progress = Progress.query.filter_by(
                user_id=joueur.id,
                enigme_id=enigme.id
            ).first()

            if enigme.manche not in progression:
                progression[enigme.manche]          = {}
                progression_enigmes[enigme.manche]  = {}
                progression_attempts[enigme.manche] = {}

            progression[enigme.manche][enigme.enigme]         = progress
            progression_enigmes[enigme.manche][enigme.enigme] = enigme
            progression_attempts[enigme.manche][enigme.enigme] = (
                progress.attempts.all() if progress else []
            )

            if progress and progress.is_solved:
                resolues += 1

        result.append({
            "user":                   joueur,
            "total_resolues":         resolues,
            "total_enigmes":          total,
            "progression":            progression,
            "progression_enigmes":    progression_enigmes,
            "progression_attempts":   progression_attempts
        })

    return result

def creer_joueur(name, password):
    """Crée un nouveau joueur. Retourne (user, erreur)."""
    if User.query.filter_by(name=name).first():
        return None, "Ce nom est déjà pris."
    user = User(name=name, password=hash_password(password), role="player")
    db.session.add(user)
    db.session.commit()
    return user, None

def reinitialiser_progression(user_id):
    """Supprime tous les Progress et Attempts d'un joueur."""
    progresses = Progress.query.filter_by(user_id=user_id).all()
    for progress in progresses:
        Attempt.query.filter_by(progress_id=progress.id).delete()
    Progress.query.filter_by(user_id=user_id).delete()
    db.session.commit()

def supprimer_joueur(user_id):
    """Supprime un joueur, sa progression et ses tentatives."""
    reinitialiser_progression(user_id)
    User.query.filter_by(id=user_id).delete()
    db.session.commit()

def toggler_indice(user_id, enigme_id):
    """Active ou désactive l'indice pour un joueur sur une énigme."""
    progress = Progress.query.filter_by(
        user_id=user_id,
        enigme_id=enigme_id
    ).first()
    if progress:
        progress.indice_active = not progress.indice_active
        db.session.commit()