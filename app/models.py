from flask_login import UserMixin
from .extensions import db
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role     = db.Column(db.String(20), nullable=False, default="player")

    # Relation : un user a plusieurs Progress
    progresses = db.relationship("Progress", back_populates="user", lazy="dynamic")

    def __repr__(self):
        return f"<User {self.name} ({self.role})>"

    @property
    def is_admin(self):
        return self.role == "admin"

# class Quete(db.Model):
#     __tablename__ = "quetes"

#     id          = db.Column(db.Integer, primary_key=True)
#     name        = db.Column(db.String(120), nullable=False)
#     description = db.Column(db.Text, nullable=False)

#     def __repr__(self):
#         return f"<{self.name}>"
    

class Manche(db.Model):
    __tablename__ = "manches"

    id        = db.Column(db.Integer, primary_key=True)
    name      = db.Column(db.String(120), nullable=False)
    video_fin = db.Column(db.String(255), nullable=True)
    # quete     = db.Column(db.Integer, db.ForeignKey("quetes.id"), nullable=False)

    enigmes   = db.relationship("Enigme", back_populates="manche_rel",
                                order_by="Enigme.enigme")
    # quete_rel = db.relationship("Quete", back_populates="manches")

    def __repr__(self):
        return f"<Manche {self.id}>"


class Enigme(db.Model):
    __tablename__ = "enigmes"

    id          = db.Column(db.Integer, primary_key=True)
    manche      = db.Column(db.Integer, db.ForeignKey("manches.id"), nullable=False)
    enigme      = db.Column(db.Integer, nullable=False)
    name        = db.Column(db.String(120), nullable=False)
    instruction = db.Column(db.Text, nullable=False)
    video_url   = db.Column(db.String(255), nullable=True)
    indice      = db.Column(db.Text, nullable=True)
    response    = db.Column(db.String(255), nullable=False)

    manche_rel  = db.relationship("Manche", back_populates="enigmes")
    progresses  = db.relationship("Progress", back_populates="enigme", lazy="dynamic")

    __table_args__ = (
        db.UniqueConstraint("manche", "enigme", name="uq_manche_enigme"),
    )

    def __repr__(self):
        return f"<Enigme M{self.manche}-E{self.enigme} — {self.name}>"

class Progress(db.Model):
    __tablename__ = "progress"

    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    enigme_id = db.Column(db.Integer, db.ForeignKey("enigmes.id"), nullable=False)
    attempt   = db.Column(db.Integer, default=0, nullable=False)
    start     = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end       = db.Column(db.DateTime, nullable=True)   # null = pas encore réussi
    time      = db.Column(db.Integer, nullable=True)    # secondes, null = pas encore réussi
    indice_active = db.Column(db.Boolean, default=False, server_default="0", nullable=False)
    
    # Relations inverses
    user   = db.relationship("User", back_populates="progresses")
    enigme = db.relationship("Enigme", back_populates="progresses")
    attempts = db.relationship("Attempt", back_populates="progress",
                               order_by="Attempt.date", lazy="dynamic")

    # Contrainte : un seul Progress par (user, enigme)
    __table_args__ = (
        db.UniqueConstraint("user_id", "enigme_id", name="uq_user_enigme"),
    )

    def __repr__(self):
        return f"<Progress user={self.user_id} enigme={self.enigme_id} attempts={self.attempt}>"

    @property
    def is_solved(self):
        return self.end is not None

    def solve(self):
        """Marque l'énigme comme résolue et calcule le temps."""
        self.end = datetime.utcnow()
        self.time = int((self.end - self.start).total_seconds())

#Indique les manches débloquées
class Config(db.Model):
    """Table clé/valeur pour la configuration globale de l'application."""
    __tablename__ = "config"

    key   = db.Column(db.String(80), primary_key=True)
    value = db.Column(db.String(255), nullable=False)

    @staticmethod
    def get(key, default=None):
        entry = Config.query.get(key)
        return entry.value if entry else default

    @staticmethod
    def set(key, value):
        entry = Config.query.get(key)
        if entry:
            entry.value = str(value)
        else:
            entry = Config(key=key, value=str(value))
            db.session.add(entry)
        db.session.commit()

class Attempt(db.Model):
    __tablename__ = "attempts"

    id          = db.Column(db.Integer, primary_key=True)
    progress_id = db.Column(db.Integer, db.ForeignKey("progress.id"), nullable=False)
    valeur      = db.Column(db.String(255), nullable=False)  # réponse brute du joueur
    date        = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    progress = db.relationship("Progress", back_populates="attempts")