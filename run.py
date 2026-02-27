from flask import Flask
from flask_jwt_extended import JWTManager
from app.infrastructure.database import db
from app.api.routes import register_routes
from app.domain.user import bcrypt

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    app.config["JWT_SECRET_KEY"] = "chave-super-simples"

    db.init_app(app)
    bcrypt.init_app(app)
    jwt = JWTManager(app)
    register_routes(app)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)