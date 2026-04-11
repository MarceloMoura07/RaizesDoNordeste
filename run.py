from flask import Flask
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from app.infrastructure.database import db
from app.api.routes import register_routes
from app.domain.user import bcrypt
from app.domain.pedido import Pedido
from app.domain.pedido_item import PedidoItem


# Factory da aplicação Flask: centraliza a configuração e inicialização das extensões
def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")


    db.init_app(app)
    bcrypt.init_app(app)
    jwt = JWTManager(app)

    # Registro das rotas da API
    register_routes(app)

    # Configuração do Swagger para documentação automática da API
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs/"
    }

    swagger_template = {
        "info": {
            "title": "API de Restaurante Raízes do Nordeste",
            "description": "API REST para gerenciamento de pedidos, produtos, unidades e programa de fidelidade.",
            "version": "1.0",
            "contact": {
                "name": "Marcelo Moura"
            }
        },
        "securityDefinitions": {
            "BearerAuth": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Digite: Bearer <seu_token>"
            }
        }
    }

    Swagger(app, config=swagger_config, template=swagger_template)

    # Cria automaticamente as tabelas do banco ao iniciar a aplicação
    with app.app_context():
        db.create_all()

    return app

app = create_app()

# Executa a aplicação em modo de desenvolvimento
if __name__ == "__main__":
    app.run(debug=True)