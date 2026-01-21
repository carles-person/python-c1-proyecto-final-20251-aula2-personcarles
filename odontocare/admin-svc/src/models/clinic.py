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

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'status': self.status,
        }
    def __repr__(self) -> str:
        return f'<clinic: {self.name}(id={self.id})>'


