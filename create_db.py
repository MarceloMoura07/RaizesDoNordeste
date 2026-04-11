from run import app
from app.infrastructure.database import db
from app.domain.unidade import Unidade
from app.domain.product import Product

with app.app_context():
    db.create_all()
    print("Banco criado com sucesso!")