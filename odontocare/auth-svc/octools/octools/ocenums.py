from enum import StrEnum

class OCROL(StrEnum):
    """
    OdontoCare user roles names
    """
    ADMIN = 'admin'
    PATIENT = 'patient'
    DOCTOR = 'doctor'
    ASSISTANT = 'assistant'


class OCENT(StrEnum):
    """
    Odontocare Entity Lists Names
    """
    DOCTOR = 'doctor'
    PATIENT = 'patient'
    CLINIC = 'clinic'

