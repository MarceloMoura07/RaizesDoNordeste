from flask import request
from app.infrastructure.database import db
from app.domain.user import User
from app.domain.user import bcrypt

def register_routes(app):

    @app.route("/")
    def home():
        return {"message": "API Raizes do Nordeste rodando"}

    from flask import request

    @app.route('/register', methods=['POST'])
    def register():
        data = request.get_json()

        if not data:
            return {"erro": "JSON não recebido"}, 400

        nome = data.get("nome")
        email = data.get("email")
        password = data.get("password")

        if not nome or not email or not password:
            return {"erro": "Dados incompletos"}, 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(
            nome=nome,
            email=email,
            senha=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return {"message": "Usuário criado com sucesso"}, 201