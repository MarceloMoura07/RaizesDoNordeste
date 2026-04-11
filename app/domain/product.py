from app.infrastructure.database import db

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)

    unidade_id = db.Column(db.Integer, db.ForeignKey("unidades.id"), nullable=False)

    unidade = db.relationship("Unidade", backref="produtos")

    estoque = db.Column(db.Integer, default=0)