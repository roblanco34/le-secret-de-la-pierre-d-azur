from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user

from .extensions import admin_required, player_required
from .models import Enigme, User
from .services import (
    get_user_by_name,
    verify_password,
    get_progression_user,
    get_or_create_progress,
    verifier_reponse,
    get_manches_debloquees,
    is_enigme_accessible,
    get_vue_globale, get_tous_les_joueurs,
    creer_joueur, reinitialiser_progression,
    get_manches_debloquees, set_manches_debloquees,
    get_intro_video_url, toggler_indice, supprimer_joueur
)



admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
auth_bp = Blueprint("auth", __name__)
game_bp = Blueprint("game", __name__)

# ── Auth ───────────────────────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Si déjà connecté, on redirige directement
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for("admin.index"))
        else:
            return redirect(url_for("game.index"))

    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        password = request.form.get("password", "")
        user     = get_user_by_name(name)

        if user and verify_password(user, password):
            login_user(user)
            if user.is_admin:
                return redirect(url_for("admin.index"))
            return redirect(url_for("game.index"))

        flash("Nom ou mot de passe incorrect.", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@game_bp.route("/")
@login_required
@player_required 
def index():
    progression = get_progression_user(current_user)
    intro_video_url = get_intro_video_url()
    return render_template("index.html", progression=progression, intro_video_url=intro_video_url)


@game_bp.route("/enigme/<int:enigme_id>", methods=["GET", "POST"])
@login_required
@player_required 
def enigme(enigme_id):
    e = Enigme.query.get_or_404(enigme_id)

    # Manche débloquée ?
    if e.manche not in get_manches_debloquees():
        flash("Cette manche n'est pas encore débloquée.", "warning")
        return redirect(url_for("game.index"))

    # Ordre respecté ?                          👈 nouveau
    if not is_enigme_accessible(current_user, e):
        flash("Tu dois terminer l'énigme précédente d'abord.", "warning")
        return redirect(url_for("game.index"))

    progress = get_or_create_progress(current_user, e)

    if request.method == "POST":
        reponse_user = request.form.get("reponse", "")
        progress, is_correct = verifier_reponse(current_user, e, reponse_user)

        if is_correct:
            flash(f"Bonne réponse ! Résolue en {progress.time/60:.0f}min.", "success")
            return redirect(url_for("game.index"))
        else:
            flash(f"Mauvaise réponse. Tentative n°{progress.attempt}.", "danger")

    return render_template("enigme.html", enigme=e, progress=progress)

# ── Admin ──────────────────────────────────────────────────────────────────────

@admin_bp.route("/")
@login_required
@admin_required
def index():
    vue = get_vue_globale()
    manches_dispo = get_manches_debloquees()
    return render_template("admin.html", vue=vue, manches_dispo=manches_dispo)

@admin_bp.route("/indice/<int:user_id>/<int:enigme_id>", methods=["POST"])
@login_required
@admin_required
def toggler_indice_route(user_id, enigme_id):
    toggler_indice(user_id, enigme_id)
    return redirect(url_for("admin.index"))

@admin_bp.route("/manche/<int:manche>/<action>")
@login_required
@admin_required
def toggle_manche(manche, action):
    """action = 'debloquer' ou 'rebloquer'"""
    if manche not in [1, 2, 3]:
        abort(404)

    manches = get_manches_debloquees()

    if action == "debloquer" and manche not in manches:
        manches.append(manche)
        manches.sort()
        flash(f"Manche {manche} débloquée.", "success")

    elif action == "rebloquer" and manche in manches:
        manches.remove(manche)
        flash(f"Manche {manche} rebloquée.", "warning")

    set_manches_debloquees(manches)
    return redirect(url_for("admin.index"))


@admin_bp.route("/joueur/creer", methods=["POST"])
@login_required
@admin_required
def creer_joueur_route():
    name     = request.form.get("name", "").strip()
    password = request.form.get("password", "").strip()

    if not name or not password:
        flash("Nom et mot de passe requis.", "danger")
        return redirect(url_for("admin.index"))

    user, erreur = creer_joueur(name, password)
    if erreur:
        flash(erreur, "danger")
    else:
        flash(f"Joueur '{user.name}' créé.", "success")

    return redirect(url_for("admin.index"))


@admin_bp.route("/joueur/<int:user_id>/reinitialiser", methods=["POST"])
@login_required
@admin_required
def reinitialiser_route(user_id):
    user = User.query.get_or_404(user_id)
    reinitialiser_progression(user_id)
    flash(f"Progression de '{user.name}' réinitialisée.", "warning")
    return redirect(url_for("admin.index"))

@admin_bp.route("/joueur/<int:user_id>/supprimer", methods=["POST"])
@login_required
@admin_required
def supprimer_joueur_route(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash("Impossible de supprimer un administrateur.", "danger")
        return redirect(url_for("admin.index"))
    supprimer_joueur(user_id)
    flash(f"Joueur '{user.name}' supprimé.", "danger")
    return redirect(url_for("admin.index"))