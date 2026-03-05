from app.infrastructure.database import db

class Estoque(db.Model):
    __tablename__ = "estoques"

    id = db.Column(db.Integer, primary_key=True)

    produto_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)

    quantidade = db.Column(db.Integer, nullable=False)

    produto = db.relationship("Product")