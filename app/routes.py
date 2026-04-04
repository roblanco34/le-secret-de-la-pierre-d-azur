from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user

from .models import Enigme
from .services import (
    get_user_by_name,
    verify_password,
    get_progression_user,
    get_or_create_progress,
    verifier_reponse,
    get_manches_debloquees,
    is_enigme_accessible
)


auth_bp = Blueprint("auth", __name__)
game_bp = Blueprint("game", __name__)

# ── Auth ───────────────────────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Si déjà connecté, on redirige directement
    if current_user.is_authenticated:
        return redirect(url_for("game.index"))

    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        password = request.form.get("password", "")
        user     = get_user_by_name(name)

        if user and verify_password(user, password):
            login_user(user)
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
def index():
    progression = get_progression_user(current_user)
    return render_template("index.html", progression=progression)


@game_bp.route("/enigme/<int:enigme_id>", methods=["GET", "POST"])
@login_required
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
            flash(f"Bonne réponse ! Résolue en {progress.time}s.", "success")
            return redirect(url_for("game.index"))
        else:
            flash(f"Mauvaise réponse. Tentative n°{progress.attempt}.", "danger")

    return render_template("enigme.html", enigme=e, progress=progress)
