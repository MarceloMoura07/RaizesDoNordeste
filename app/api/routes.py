from flask import request
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.infrastructure.database import db
from app.domain.user import User, bcrypt
from sqlalchemy import func
from app.domain.product import Product
from app.domain.pedido import Pedido
from app.domain.pedido_item import PedidoItem
from app.domain.pedido import STATUS_PEDIDO
from app.domain.product import Product
from datetime import datetime

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
        role = data.get("role", "CLIENTE")  # 🔹 novo campo opcional

        if not nome or not email or not password:
            return {"erro": "Dados incompletos"}, 400

        # 🔹 Evita criar usuário duplicado
        if User.query.filter_by(email=email).first():
            return {"erro": "E-mail já cadastrado"}, 409

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(
            nome=nome,
            email=email,
            senha=hashed_password,
            role=role
        )

        db.session.add(new_user)
        db.session.commit()

        return {
            "message": "Usuário criado com sucesso",
            "role": new_user.role
        }, 201


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

        user_id = int(get_jwt_identity())

        novo_pedido = Pedido(
            user_id=user_id,
            unidade_id=unidade_id,
            canal=canal
        )

        db.session.add(novo_pedido)
        db.session.flush()  # garante que já temos o ID sem precisar commit

        total = 0

        for item in itens:

            produto = Product.query.get(item["produto_id"])

            if not produto:
                return {"erro": "Produto não encontrado"}, 404

            quantidade = item.get("quantidade")

            if not quantidade or quantidade <= 0:
                return {"erro": "Quantidade inválida"}, 400

            if produto.estoque < quantidade:
                return {"erro": "Estoque insuficiente"}, 409

            preco_unitario = produto.preco

            pedido_item = PedidoItem(
                pedido_id=novo_pedido.id,
                produto_id=produto.id,
                quantidade=quantidade,
                preco_unitario=preco_unitario
            )

            db.session.add(pedido_item)

            produto.estoque -= quantidade

            total += quantidade * preco_unitario

        novo_pedido.valor_total = total

        db.session.commit()

        return {
            "message": "Pedido criado com sucesso",
            "pedido_id": novo_pedido.id,
            "valor_total": novo_pedido.valor_total
        }, 201



    @app.route('/pedidos', methods=['GET'])
    @jwt_required()
    def listar_pedidos():

        canal = request.args.get("canalPedido")

        query = Pedido.query

        if canal:
            query = query.filter_by(canal=canal)

        pedidos = query.all()

        resultado = []

        for pedido in pedidos:
            resultado.append({
                "id": pedido.id,
                "canal": pedido.canal,
                "status": pedido.status
            })

        return resultado, 200


    @app.route('/pedido/<int:pedido_id>/status', methods=['PUT'])
    @jwt_required()
    def atualizar_status(pedido_id):

        data = request.get_json()
        novo_status = data.get("status")

        if not novo_status:
            return {"erro": "Status não informado"}, 400

        if novo_status not in STATUS_PEDIDO:
            return {"erro": "Status inválido"}, 400

        pedido = Pedido.query.get(pedido_id)

        if not pedido:
            return {"erro": "Pedido não encontrado"}, 404

        # Fluxo permitido de status
        transicoes_permitidas = {
            "pendente": ["pago", "cancelado"],
            "pago": ["cozinha", "cancelado"],
            "cozinha": ["pronto"],
            "pronto": ["entregue"],
            "entregue": [],
            "cancelado": []
        }

        status_atual = pedido.status

        if novo_status not in transicoes_permitidas.get(status_atual, []):
            return {
                "erro": f"Transição inválida de '{status_atual}' para '{novo_status}'"
            }, 400

        pedido.status = novo_status
        db.session.commit()

        return {
            "message": "Status atualizado com sucesso",
            "status_atual": pedido.status
        }, 200

    @app.route('/pedido/<int:pedido_id>/cancelar', methods=['PUT'])
    @jwt_required()
    def cancelar_pedido(pedido_id):

        pedido = Pedido.query.get(pedido_id)

        if not pedido:
            return {"erro": "Pedido não encontrado"}, 404

        pedido.status = "cancelado"
        db.session.commit()

        return {"message": "Pedido cancelado com sucesso"}, 200


    @app.route('/meus-pedidos', methods=['GET'])
    @jwt_required()
    def meus_pedidos():

        user_id = int(get_jwt_identity())

        pedidos = Pedido.query.filter_by(user_id=user_id).all()

        resultado = []

        for pedido in pedidos:
            resultado.append({
                "id": pedido.id,
                "unidade_id": pedido.unidade_id,
                "status": pedido.status,
                "canal": pedido.canal,
                "valor_total": pedido.valor_total
            })

        return resultado, 200


    @app.route('/unidades/<int:unidade_id>/pedidos', methods=['GET'])
    @jwt_required()
    def pedidos_por_unidade(unidade_id):

        pedidos = Pedido.query.filter_by(unidade_id=unidade_id).all()

        resultado = []

        for pedido in pedidos:
            resultado.append({
                "id": pedido.id,
                "user_id": pedido.user_id,
                "status": pedido.status,
                "canal": pedido.canal,
                "valor_total": pedido.valor_total
            })

        return resultado, 200



    @app.route('/estoque/<int:produto_id>', methods=['PUT'])
    @jwt_required()
    def atualizar_estoque(produto_id):

        data = request.get_json()
        quantidade = data.get("quantidade")

        if quantidade is None:
            return {"erro": "Quantidade não informada"}, 400

        produto = Product.query.get(produto_id)

        if not produto:
            return {"erro": "Produto não encontrado"}, 404

        produto.estoque = quantidade
        db.session.commit()

        return {"message": "Estoque atualizado com sucesso"}, 200


    @app.route('/pedidos/<int:pedido_id>/pagamento', methods=['POST'])
    @jwt_required()
    def pagamento_mock(pedido_id):

        data = request.get_json()
        resultado = data.get("resultado")

        if not resultado:
            return {"erro": "Resultado não informado"}, 400

        pedido = Pedido.query.get(pedido_id)

        if not pedido:
            return {"erro": "Pedido não encontrado"}, 404

        if pedido.status != "pendente":
            return {"erro": "Pedido já processado"}, 409

        if resultado == "aprovado":
            pedido.status = "pago"
            pedido.data_pagamento = datetime.utcnow()

        elif resultado == "recusado":
            pedido.status = "cancelado"

        else:
            return {"erro": "Resultado inválido"}, 400

        db.session.commit()

        return {
            "message": "Pagamento aprovado",
            "pedido_id": pedido.id,
            "status": pedido.status
        }, 200