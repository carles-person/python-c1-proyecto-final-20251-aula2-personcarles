""" Init file pels models del servei ADMIN
Estan per separat per si algun dia es volgués moure algun dels models 
a una altra base de dades
"""
__version__ = '0.1.0'
from .database import db
from .clinic import Clinic
from .doctor import Doctor
from .patient import Patient

