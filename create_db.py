from run import app
from app.infrastructure.database import db

with app.app_context():
    db.create_all()
    print("Banco criado com sucesso!")