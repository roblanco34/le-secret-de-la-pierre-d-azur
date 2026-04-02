from flask import Blueprint, render_template, request, session, redirect
from .game import get_current_enigme, check_answer

main = Blueprint('main', __name__)

@main.route("/", methods=["GET", "POST"])
def game():
    team_id = session.get("team_id", 1)

    enigme = get_current_enigme(team_id)

    if request.method == "POST":
        answer = request.form["answer"]

        if check_answer(team_id, answer):
            return redirect("/")
        else:
            return render_template("game.html", question=enigme, error="Faux")

    return render_template("game.html", question=enigme)