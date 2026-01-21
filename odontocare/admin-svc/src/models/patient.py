from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import mapped_column, Mapped
from . import db

# defineixo classe Patient per ORM
class Patient(db.Model):
    __tablename__ = 'patients'
    id:Mapped[int] = mapped_column(Integer, primary_key=True)

    # id_user: FK a Auth-Service -> accessible via REST
    id_user:Mapped[int] = mapped_column(Integer, nullable=True)

    name:Mapped[str] = mapped_column(String(64), nullable=False)
    phone:Mapped[str] = mapped_column(String(16), nullable=False)
    status:Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.id_user,
            'name': self.name,
            'phone': self.phone,
            'status': self.status,
        }
    
    def __repr__(self) -> str:
        return f'<patient: {self.name}(id={self.id})(user_id={self.id_user})>'


