"""
Docstring for odontocare.api-gateway.bp.agenda_bp
"""

from flask import Blueprint, request

agenda_bp = Blueprint('agenda_bp',__name__)
AGENDA_SVC

@agenda_bp.route(('/',methods=['GET']))
def get_appointment():
    app_date = request.args.get('date','')
    app_time = request.args.get('time','')
    doctor_id = request.args.get('doctor')
    patient_id = request.args.get('patient')
    
    try: