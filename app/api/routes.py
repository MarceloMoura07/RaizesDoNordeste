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
from logs import logger



def register_routes(app):

    @app.route("/")
    def home():
        return {"message": "API Raizes do Nordeste rodando"}

    from flask import request
    from app.domain.unidade import Unidade

    @app.route('/unidades', methods=['POST'])
    @jwt_required()
    def criar_unidade():
        """
    Cria uma nova unidade
    ---
    tags:
      - Unidades
    description: Cria uma nova unidade da empresa informando nome e cidade.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - nome
            - cidade
          properties:
            nome:
              type: string
              example: Unidade Recife
            cidade:
              type: string
              example: Recife
    responses:
      201:
        description: Unidade criada com sucesso
        schema:
          type: object
          properties:
            message:
              type: string
              example: Unidade criada com sucesso
      400:
        description: Dados incompletos
      401:
        description: Token JWT ausente ou inválido
    """

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
        """
            Cadastro de novo usuário
            ---
            tags:
              - Autenticação
            description: Cria um novo usuário no sistema
            parameters:
              - in: body
                name: body
                required: true
                schema:
                  type: object
                  required:
                    - nome
                    - email
                    - password
                  properties:
                    nome:
                      type: string
                      example: João Silva
                    email:
                      type: string
                      example: joao@email.com
                    password:
                      type: string
                      example: 123456
                    role:
                      type: string
                      example: CLIENTE
                      description: Papel do usuário no sistema (opcional)
            responses:
              201:
                description: Usuário criado com sucesso
              400:
                description: Dados incompletos ou JSON inválido
              409:
                description: E-mail já cadastrado
            """
        data = request.get_json()

        if not data:
            return {"erro": "JSON não recebido"}, 400

        nome = data.get("nome")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role", "CLIENTE")  # 🔹 novo campo opcional

        if not nome or not email or not password:
            return {"erro": "Dados incompletos"}, 400


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

        logger.info(f"Novo usuário criado: {email}")

        return {
            "message": "Usuário criado com sucesso",
            "role": new_user.role
        }, 201


    @app.route('/login', methods=['POST'])
    def login():
        """
            Login do usuário
            ---
            tags:
              - Autenticação
            description: Autentica um usuário e retorna um token JWT para acessar rotas protegidas
            parameters:
              - in: body
                name: body
                required: true
                schema:
                  type: object
                  required:
                    - email
                    - password
                  properties:
                    email:
                      type: string
                      example: usuario@email.com
                    password:
                      type: string
                      example: 123456
            responses:
              200:
                description: Login realizado com sucesso
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: Login realizado com sucesso
                    access_token:
                      type: string
                      example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
              400:
                description: Dados incompletos ou JSON não enviado
              401:
                description: Senha incorreta
              404:
                description: Usuário não encontrado
            """
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

        logger.info(f"Login realizado: {email}")

        return {
            "message": "Login realizado com sucesso",
            "access_token": access_token
        }, 200

    @app.route('/users', methods=['GET'])
    def listar_users():
        """
            Lista todos os usuários
            ---
            tags:
              - Usuários
            description: Retorna a lista de usuários cadastrados no sistema.
            responses:
              200:
                description: Lista de usuários retornada com sucesso
                schema:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                        example: 1
                      nome:
                        type: string
                        example: João Silva
                      email:
                        type: string
                        example: joao@email.com
            """

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
        """
    Cria um novo produto
    ---
    tags:
      - Produtos
    description: "Cria um novo produto associado a uma unidade."
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - nome
            - preco
            - unidade_id
          properties:
            nome:
              type: string
              example: Tapioca
            preco:
              type: number
              example: 12.50
            unidade_id:
              type: integer
              example: 1
              description: "ID da unidade onde o produto será vendido"
    responses:
      201:
        description: Produto criado com sucesso
        schema:
          type: object
          properties:
            message:
              type: string
              example: Produto criado com sucesso
      400:
        description: Dados incompletos ou JSON não enviado
      401:
        description: Token JWT ausente ou inválido
      404:
        description: Unidade não encontrada
    """

        data = request.get_json()

        if not data:
            return {"erro": "JSON não recebido"}, 400

        nome = data.get("nome")
        preco = data.get("preco")
        unidade_id = data.get("unidade_id")

        if not nome or not preco or not unidade_id:
            return {"erro": "Dados incompletos"}, 400

        unidade = Unidade.query.get(unidade_id)

        if not unidade:
            return {"erro": "Unidade não encontrada"}, 404

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
        """
    Lista produtos de uma unidade
    ---
    tags:
      - Produtos
    description: "Retorna todos os produtos disponíveis em uma unidade específica."
    parameters:
      - in: path
        name: unidade_id
        type: integer
        required: true
        description: "ID da unidade"
        example: 1
    responses:
      200:
        description: Lista de produtos retornada com sucesso
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              nome:
                type: string
                example: Tapioca
              preco:
                type: number
                example: 12.50
      404:
        description: Unidade não encontrada
    """
        unidade = Unidade.query.get(unidade_id)

        if not unidade:
            return {"erro": "Unidade não encontrada"}, 404

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
        """
            Cria um novo pedido
            ---
            tags:
              - Pedidos
            description: Cria um pedido com múltiplos itens e calcula o valor total com possível desconto.
            parameters:
              - in: body
                name: body
                required: true
                schema:
                  type: object
                  required:
                    - unidade_id
                    - canal
                    - itens
                  properties:
                    unidade_id:
                      type: integer
                      example: 1
                    canal:
                      type: string
                      example: app
                      description: "Canal do pedido (ex: app ou loja)"
                    itens:
                      type: array
                      description: Lista de produtos do pedido
                      items:
                        type: object
                        required:
                          - produto_id
                          - quantidade
                        properties:
                          produto_id:
                            type: integer
                            example: 1
                          quantidade:
                            type: integer
                            example: 2
            responses:
              201:
                description: Pedido criado com sucesso
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: Pedido criado com sucesso
                    pedido_id:
                      type: integer
                      example: 10
                    valor_total:
                      type: number
                      example: 85.50
                    desconto:
                      type: number
                      example: 8.55
              400:
                description: Dados incompletos ou pedido sem itens
              404:
                description: Unidade ou produto não encontrado
              409:
                description: Estoque insuficiente
            """

        data = request.get_json()

        unidade_id = data.get("unidade_id")
        canal = data.get("canal")
        itens = data.get("itens")

        if not unidade_id or not canal or itens is None:
            return {"erro": "Dados incompletos"}, 400

        if len(itens) == 0:
            return {"erro": "Pedido deve conter ao menos um item"}, 400

        unidade = Unidade.query.get(unidade_id)

        if not unidade:
            return {"erro": "Unidade não encontrada"}, 404

        user_id = int(get_jwt_identity())

        novo_pedido = Pedido(
            user_id=user_id,
            unidade_id=unidade_id,
            canal=canal
        )

        db.session.add(novo_pedido)
        db.session.flush()  # garante que já temos o ID sem precisar commit

        total = 0
        desconto = 0
        valor_final = 0

        for item in itens:

            produto = Product.query.get(item["produto_id"])

            if not produto:
                return {"erro": "Produto não encontrado"}, 404

            if produto.unidade_id != unidade_id:
                return {"erro": "Produto não pertence a esta unidade"}, 400

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

            desconto = 0

        if canal == "app":
            desconto = total * 0.10

        valor_final = total - desconto

        novo_pedido.valor_total = total

        user = User.query.get(user_id)

        if user.fidelidade_ativa:
            pontos_ganhos = int(total / 10)
            user.pontos += pontos_ganhos

        db.session.commit()

        logger.info(f"Pedido {novo_pedido.id} criado pelo usuário {user_id} na unidade {unidade_id}")

        return {
            "message": "Pedido criado com sucesso",
            "pedido_id": novo_pedido.id,
            "valor_total": valor_final,
            "desconto": desconto
        }, 201



    @app.route('/pedidos', methods=['GET'])
    @jwt_required()
    def listar_pedidos():
        """
            Lista pedidos
            ---
            tags:
              - Pedidos
            description: Retorna todos os pedidos cadastrados. Pode filtrar por canal do pedido.
            parameters:
              - in: query
                name: canalPedido
                type: string
                required: false
                description: "Filtra pedidos pelo canal (ex: app ou loja)"
                example: app
            responses:
              200:
                description: Lista de pedidos retornada com sucesso
                schema:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                        example: 1
                      canal:
                        type: string
                        example: app
                      status:
                        type: string
                        example: pendente
            """

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
        """
            Atualiza o status de um pedido
            ---
            tags:
              - Pedidos
            description: Atualiza o status de um pedido respeitando o fluxo permitido de transições.
            parameters:
              - in: path
                name: pedido_id
                type: integer
                required: true
                description: ID do pedido
                example: 1
              - in: body
                name: body
                required: true
                schema:
                  type: object
                  required:
                    - status
                  properties:
                    status:
                      type: string
                      example: pago
                      description: Novo status do pedido
            responses:
              200:
                description: Status atualizado com sucesso
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: Status atualizado com sucesso
                    status_atual:
                      type: string
                      example: pago
              400:
                description: Status inválido ou transição não permitida
              404:
                description: Pedido não encontrado
            """

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
        """
            Cancela um pedido
            ---
            tags:
              - Pedidos
            description: Altera o status do pedido para cancelado.
            parameters:
              - in: path
                name: pedido_id
                type: integer
                required: true
                description: ID do pedido a ser cancelado
                example: 1
            responses:
              200:
                description: Pedido cancelado com sucesso
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: Pedido cancelado com sucesso
              404:
                description: Pedido não encontrado
            """

        pedido = Pedido.query.get(pedido_id)

        if not pedido:
            return {"erro": "Pedido não encontrado"}, 404

        pedido.status = "cancelado"
        db.session.commit()

        return {"message": "Pedido cancelado com sucesso"}, 200


    @app.route('/meus-pedidos', methods=['GET'])
    @jwt_required()
    def meus_pedidos():
        """
           Lista os pedidos do usuário autenticado
           ---
           tags:
             - Pedidos
           description: Retorna todos os pedidos realizados pelo usuário logado.
           responses:
             200:
               description: Lista de pedidos do usuário
               schema:
                 type: array
                 items:
                   type: object
                   properties:
                     id:
                       type: integer
                       example: 5
                     unidade_id:
                       type: integer
                       example: 2
                     status:
                       type: string
                       example: pago
                     canal:
                       type: string
                       example: app
                     valor_total:
                       type: number
                       example: 58.90
             401:
               description: Token JWT ausente ou inválido
           """

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
        """
            Lista pedidos de uma unidade
            ---
            tags:
              - Pedidos
            description: Retorna todos os pedidos realizados em uma unidade específica.
            parameters:
              - in: path
                name: unidade_id
                type: integer
                required: true
                description: ID da unidade
                example: 1
            responses:
              200:
                description: Lista de pedidos da unidade
                schema:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                        example: 10
                      user_id:
                        type: integer
                        example: 3
                      status:
                        type: string
                        example: pago
                      canal:
                        type: string
                        example: app
                      valor_total:
                        type: number
                        example: 45.90
              401:
                description: Token JWT ausente ou inválido
            """

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
        """
            Atualiza o estoque de um produto
            ---
            tags:
              - Produtos
            description: "Atualiza a quantidade em estoque de um produto específico."
            parameters:
              - in: path
                name: produto_id
                type: integer
                required: true
                description: "ID do produto"
                example: 1
              - in: body
                name: body
                required: true
                schema:
                  type: object
                  required:
                    - quantidade
                  properties:
                    quantidade:
                      type: integer
                      example: 50
                      description: "Nova quantidade em estoque"
            responses:
              200:
                description: Estoque atualizado com sucesso
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: Estoque atualizado com sucesso
              400:
                description: Quantidade não informada
              401:
                description: Token JWT ausente ou inválido
              404:
                description: Produto não encontrado
            """

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
        """
            Processa o pagamento de um pedido
            ---
            tags:
              - Pagamentos
            description: "Simula o processamento de pagamento de um pedido. Pode retornar aprovado ou recusado."
            parameters:
              - in: path
                name: pedido_id
                type: integer
                required: true
                description: "ID do pedido"
                example: 10
              - in: body
                name: body
                required: true
                schema:
                  type: object
                  required:
                    - resultado
                  properties:
                    resultado:
                      type: string
                      example: aprovado
                      description: "Resultado do pagamento (aprovado ou recusado)"
            responses:
              200:
                description: Resultado do pagamento processado
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: Pagamento aprovado
                    pedido_id:
                      type: integer
                      example: 10
                    status:
                      type: string
                      example: pago
              400:
                description: Resultado inválido ou não informado
              401:
                description: Token JWT ausente ou inválido
              404:
                description: Pedido não encontrado
              409:
                description: Pedido já processado
            """

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
            mensagem = "Pagamento aprovado"

        elif resultado == "recusado":
            pedido.status = "cancelado"
            mensagem = "Pagamento recusado"

        else:
            return {"erro": "Resultado inválido"}, 400

        db.session.commit()

        logger.info(f"Pagamento do pedido {pedido_id} processado com resultado: {pedido.status}")

        return {
            "message": mensagem,
            "pedido_id": pedido.id,
            "status": pedido.status
        }, 200

    @app.route('/ativar-fidelidade', methods=['POST'])
    @jwt_required()
    def ativar_fidelidade():
        """
            Ativa o programa de fidelidade
            ---
            tags:
              - Fidelidade
            description: "Ativa o programa de fidelidade para o usuário autenticado."
            responses:
              200:
                description: Programa de fidelidade ativado com sucesso
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: Programa de fidelidade ativado
              401:
                description: Token JWT ausente ou inválido
              404:
                description: Usuário não encontrado
            """

        user_id = int(get_jwt_identity())

        user = User.query.get(user_id)

        if not user:
            return {"erro": "Usuário não encontrado"}, 404

        user.fidelidade_ativa = True

        db.session.commit()

        return {"message": "Programa de fidelidade ativado"}, 200


    @app.route('/meus-pontos', methods=['GET'])
    @jwt_required()
    def meus_pontos():
        """
            Consulta os pontos de fidelidade do usuário
            ---
            tags:
              - Fidelidade
            description: "Retorna a quantidade de pontos acumulados pelo usuário autenticado."
            responses:
              200:
                description: Pontos retornados com sucesso
                schema:
                  type: object
                  properties:
                    user_id:
                      type: integer
                      example: 3
                    pontos:
                      type: integer
                      example: 120
              401:
                description: Token JWT ausente ou inválido
              404:
                description: Usuário não encontrado
            """

        user_id = int(get_jwt_identity())

        user = User.query.get(user_id)

        if not user:
            return {"erro": "Usuário não encontrado"}, 404

        return {
            "user_id": user.id,
            "pontos": user.pontos
        }, 200

    @app.route('/resgatar-pontos', methods=['POST'])
    @jwt_required()
    def resgatar_pontos():
        """
            Resgata pontos de fidelidade
            ---
            tags:
              - Fidelidade
            description: "Permite ao usuário trocar pontos acumulados por desconto."
            parameters:
              - in: body
                name: body
                required: true
                schema:
                  type: object
                  required:
                    - pontos
                  properties:
                    pontos:
                      type: integer
                      example: 20
                      description: "Quantidade de pontos a resgatar (deve ser múltiplo de 10)"
            responses:
              200:
                description: Pontos resgatados com sucesso
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: Pontos resgatados com sucesso
                    pontos_utilizados:
                      type: integer
                      example: 20
                    desconto:
                      type: number
                      example: 10
                    pontos_restantes:
                      type: integer
                      example: 80
              400:
                description: Quantidade de pontos inválida
              401:
                description: Token JWT ausente ou inválido
              404:
                description: Usuário não encontrado
              409:
                description: Pontos insuficientes
            """

        data = request.get_json()
        pontos = data.get("pontos")

        if not pontos:
            return {"erro": "Quantidade de pontos não informada"}, 400

        if pontos % 10 != 0:
            return {"erro": "Resgate deve ser múltiplo de 10 pontos"}, 400

        user_id = int(get_jwt_identity())

        user = User.query.get(user_id)

        if not user:
            return {"erro": "Usuário não encontrado"}, 404

        if user.pontos < pontos:
            return {"erro": "Pontos insuficientes"}, 409

        desconto = (pontos / 10) * 5

        user.pontos -= pontos

        db.session.commit()

        return {
            "message": "Pontos resgatados com sucesso",
            "pontos_utilizados": pontos,
            "desconto": desconto,
            "pontos_restantes": user.pontos
        }, 200