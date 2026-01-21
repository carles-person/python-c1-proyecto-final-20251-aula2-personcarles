from flask import Flask
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os

# inicialitzo la BD segons documentacio flask-sqlalchemy
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class User(db.Model):
    __tablename__ = 'users'
    id:Mapped[int] = mapped_column(primary_key=True)
    username:Mapped[str] = mapped_column(String(32),unique=True, nullable=False)
    #TODO: comprobar longitud del hash del password per ajustar el camp.
    password:Mapped[str] = mapped_column(String(200), nullable=False) # hashed
    role:Mapped[str] = mapped_column(String(10), nullable=False) # admin, assist, doctor, patient

    def to_dict(self):
        return {'id': self.id, 'username': self.username, 'role': self.role}
    
    def __repr__(self):
        return f'<user: {self.username}(id={self.id})>'

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///test.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  

    db.init_app(app)
    with app.app_context():
        db.create_all()

print(os.environ.get("OC_TEST","AIXO NO VAL"))

head = {
    'Content-Type': 'application/json'
}

payload = {
    "username": "admin",
    "password": "admin"
}

import requests
response = requests.post('http://localhost:4001/login', headers=head,json=payload)

print(response.headers)
print(response.text) c

token = response.json().get('token','no')
print("tocken-->",token)
head = {
    'Content-Type': 'application/json', 
    'Authorization': f'Bearer {token}'
}

response = requests.get('http://localhost:4001/validate/1', headers=head)
print('-------------')
print(response.json())

