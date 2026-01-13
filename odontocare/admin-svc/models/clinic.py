from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import mapped_column, Mapped
from . import db

# defineixo classe Clinica
class Clinic(db.Model):
    __tablename__ = 'clinics'
    id:Mapped[int] = mapped_column(Integer, primary_key=True)

    name:Mapped[str] = mapped_column(String(64), nullable=False)
    address:Mapped[str] = mapped_column(String(128), nullable=False)
    status:Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


