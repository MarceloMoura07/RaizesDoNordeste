from app.infrastructure.database import db
from datetime import datetime

STATUS_PEDIDO = [
        "pendente",
        "pago",
        "cozinha",
        "pronto",
        "entregue",
        "cancelado"
    ]

class Pedido(db.Model):
    __tablename__ = "pedidos"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    unidade_id = db.Column(db.Integer, db.ForeignKey("unidades.id"), nullable=False)

    canal = db.Column(db.String(50), nullable=False)

    status = db.Column(db.String(50), default="pendente")

    valor_total = db.Column(db.Float, default=0.0)

    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    data_pagamento = db.Column(db.DateTime)

    itens = db.relationship("PedidoItem", backref="pedido", lazy=True)

def calcular_total(self):
    total = 0

    for item in self.itens:
        total += item.quantidade * item.preco_unitario

    self.valor_total = total