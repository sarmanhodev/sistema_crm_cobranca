from tables import *
from main import app, db

print("Criando a base de dados..."+"\n")

with app.app_context():
    db.create_all()

print("\n"+"Base de dados criada com sucesso"+"\n")