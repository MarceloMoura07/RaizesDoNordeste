from app.infrastructure.database import db

class PedidoItem(db.Model):
    __tablename__ = "pedido_itens"

    id = db.Column(db.Integer, primary_key=True)

    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)

    quantidade = db.Column(db.Integer, nullable=False)