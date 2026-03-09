from app.infrastructure.database import db
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="CLIENTE")

    fidelidade_ativa = db.Column(db.Boolean, default=False)
    pontos = db.Column(db.Integer, default=0)

    def set_senha(self, senha):
        self.senha = bcrypt.generate_password_hash(senha).decode('utf-8')

    def check_senha(self, senha):
        return bcrypt.check_password_hash(self.senha, senha)