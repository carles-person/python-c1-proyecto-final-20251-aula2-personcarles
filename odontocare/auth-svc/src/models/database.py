"""
Docstring for odontocare.auth-svc.models.database
"""

# inicialitzo la BD segons documentacio flask-sqlalchemy
from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)