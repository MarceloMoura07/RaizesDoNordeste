from flask import request
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.infrastructure.database import db
from app.domain.user import User, bcrypt
from sqlalchemy import func
from app.domain.product import Product
from app.domain.pedido import Pedido
from app.domain.pedido_item import PedidoItem

def register_routes(app):

    @app.route("/")
    def home():
        return {"message": "API Raizes do Nordeste rodando"}

    from flask import request
    from app.domain.unidade import Unidade

    @app.route('/unidades', methods=['POST'])
    @jwt_required()
    def criar_unidade():
        data = request.get_json()

        nome = data.get("nome")
        cidade = data.get("cidade")

        if not nome or not cidade:
            return {"erro": "Dados incompletos"}, 400

        nova_unidade = Unidade(nome=nome, cidade=cidade)

        db.session.add(nova_unidade)
        db.session.commit()

        return {"message": "Unidade criada com sucesso"}, 201

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



    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()

        if not data:
            return {"erro": "JSON não recebido"}, 400

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return {"erro": "Dados incompletos"}, 400

        user = User.query.filter(func.lower(User.email) == email.lower()).first()

        if not user:
            return {"erro": "Usuário não encontrado"}, 404

        if not bcrypt.check_password_hash(user.senha, password):
            return {"erro": "Senha incorreta"}, 401

        access_token = create_access_token(identity=str(user.id))

        return {
            "message": "Login realizado com sucesso",
            "access_token": access_token
        }, 200

    @app.route('/users', methods=['GET'])
    def listar_users():
        users = User.query.all()

        resultado = []

        for user in users:
            resultado.append({
                "id": user.id,
                "nome": user.nome,
                "email": user.email
            })

        return resultado

    # @app.route('/perfil', methods=['GET'])
    # @jwt_required()
    # def perfil():
    #     user_id = get_jwt_identity()
    #
    #     user = User.query.get(int(user_id))
    #
    #     if not user:
    #         return {"erro": "Usuário não encontrado"}, 404
    #
    #     return {
    #         "id": user.id,
    #         "nome": user.nome,
    #         "email": user.email
    #     }, 200

    @app.route('/produtos', methods=['POST'])
    @jwt_required()
    def criar_produto():
        data = request.get_json()

        if not data:
            return {"erro": "JSON não recebido"}, 400

        nome = data.get("nome")
        preco = data.get("preco")
        unidade_id = data.get("unidade_id")

        if not nome or not preco or not unidade_id:
            return {"erro": "Dados incompletos"}, 400

        novo_produto = Product(
            nome=nome,
            preco=preco,
            unidade_id=unidade_id
        )

        db.session.add(novo_produto)
        db.session.commit()

        return {"message": "Produto criado com sucesso"}, 201

    @app.route('/unidades/<int:unidade_id>/produtos', methods=['GET'])
    def listar_produtos(unidade_id):

        produtos = Product.query.filter_by(unidade_id=unidade_id).all()

        resultado = []

        for produto in produtos:
            resultado.append({
                "id": produto.id,
                "nome": produto.nome,
                "preco": produto.preco
            })

        return resultado, 200

    @app.route('/pedidos', methods=['POST'])
    @jwt_required()
    def criar_pedido():

        data = request.get_json()

        unidade_id = data.get("unidade_id")
        canal = data.get("canal")
        itens = data.get("itens")

        if not unidade_id or not canal or not itens:
            return {"erro": "Dados incompletos"}, 400

        user_id = get_jwt_identity()

        novo_pedido = Pedido(
            user_id=user_id,
            unidade_id=unidade_id,
            canal=canal
        )

        db.session.add(novo_pedido)
        db.session.commit()

        for item in itens:
            produto = Product.query.get(item["produto_id"])

            if not produto:
                return {"erro": "Produto não encontrado"}, 404

            pedido_item = PedidoItem(
                pedido_id=novo_pedido.id,
                produto_id=produto.id,
                quantidade=item["quantidade"]
            )

            db.session.add(pedido_item)

        db.session.commit()

        return {"message": "Pedido criado com sucesso"}, 201

    @app.route('/meus-pedidos', methods=['GET'])
    @jwt_required()
    def listar_meus_pedidos():

        user_id = get_jwt_identity()

        pedidos = Pedido.query.filter_by(user_id=user_id).all()

        resultado = []

        for pedido in pedidos:
            resultado.append({
                "id": pedido.id,
                "unidade_id": pedido.unidade_id,
                "canal": pedido.canal,
                "status": pedido.status,
                "data_criacao": pedido.data_criacao
            })

        return resultado, 200