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


class Enigme(db.Model):
    __tablename__ = "enigmes"

    id          = db.Column(db.Integer, primary_key=True)  # ordre global 1→15
    manche      = db.Column(db.Integer, nullable=False)    # 1, 2 ou 3
    enigme      = db.Column(db.Integer, nullable=False)    # 1→5 dans la manche
    name        = db.Column(db.String(120), nullable=False)
    instruction = db.Column(db.Text, nullable=False)
    video_url   = db.Column(db.String(255), nullable=True)
    response    = db.Column(db.String(255), nullable=False)  # stockée normalisée
    indice      = db.Column(db.Text, nullable=True)

    # Relation : une énigme a plusieurs Progress
    progresses = db.relationship("Progress", back_populates="enigme", lazy="dynamic")

    # Contrainte : combinaison manche+enigme unique
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