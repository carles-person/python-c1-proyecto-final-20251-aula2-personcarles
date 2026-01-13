"""
Docstring for odontocare.auth-svc.models
"""

from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped
from .database import db

# defineixo la classe usuari
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
    
