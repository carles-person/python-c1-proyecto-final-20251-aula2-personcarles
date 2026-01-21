from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import  mapped_column, Mapped
from . import db

# defineixo classe Doctor pel ORM
class Doctor(db.Model):
    __tablename__ = 'doctors'
    id:Mapped[int] = mapped_column(Integer, primary_key=True)

    # id_user: FK a Auth-Service -> accessible via REST
    id_user:Mapped[int] = mapped_column(Integer, nullable=True)

    name:Mapped[str] = mapped_column(String(64), nullable=False)
    speciality:Mapped[str] = mapped_column(String(32), nullable=False)
    status:Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.id_user,
            'name': self.name,
            'speciality': self.speciality,
            'status': self.status,
        }
    def __repr__(self) -> str:
        return f'<doctor: {self.name}(id={self.id})(user_id={self.id_user})>'



