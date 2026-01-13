import os
from http import HTTPStatus
from flask import Flask, request, jsonify
import requests
from models import Appointment
from models import db

from tools import role_required, token_required, OCENT, OCERR, OCROL, json_error,json_message

def create_app():
    app = Flask(__name__)
    # configuro les variables
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///agenda.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('OC_SECRET_KEY', 'development_secret')
    app.config['AGENDA_LISTEN_HOST'] = os.environ.get('AGENDA_LISTEN_HOST', '0.0.0.0')
    app.config['AGENDA_LISTEN_PORT'] = os.environ.get('AGENDA_LISTEN_PORT', 4003)

    app.config['AUTH_SVC'] = os.environ.get('AUTH_SVC','http://localhost:4001')
    app.config['ADMIN_SVC'] = os.environ.get('AUTH_SVC','http://localhost:4002')

    # Creo les taules a la BD
    db.init_app(app)
    with app.app_context():
        db.create_all()

    """ 
    Defineixo els endpoints per cada un dels microserveis:
    - creacio d'una cita
    - modificació d'una cita
    - cancel·lació d'una cita
    - visualització de cites existents
    -
    """

    # Endpoint per defecte. retorna un valor no especificat
    @app.route('/', methods =['GET', 'POST', 'PUT'])
    def default():
        return json_error(HTTPStatus.NOT_IMPLEMENTED)
    
    @app.route('/health', methods=['GET'])
    def health():
        return json_message(HTTPStatus.OK, 'OK: System Online'), HTTPStatus.OK
    
    # lista les cites
    @app.route('/list', methods=['GET'])
    def get_agenda():
        pass
    
    # afegeix una nova cita
    @app.route('/add', methods = ['POST'])
    def create_appointment():

        def check_entity(entity_type:str,entity_id:int)->bool:
            """
            Comprobo que la entitat (doctor, patient, clinic) amb <id> existeixen en 
            la base de dades (attenció: utilitzem REST service)
            Parameters
            ----------
            entity_type : str
                Entity de tipus "doctor", "clinic" o "patient"
            entity_id : int
                <id> de l'entitat a la DB.
            
            Returns:
            --------
            bool:
                True si s'ha trobat l'entitat
                False: si no s'ha trobat o hi ha un problema amb la communicació
            """
            try:
                response = requests.get(app.config['AUTH_URL']+f'/check?entity={entity_type}t&id={entity_id}')
                response.raise_for_status()
                data = response.json()
                if data['status']:
                    return True
                else:
                    return False

            except:
                return False


        def check_conflicts(doctor_id, patient_id, start_date, end_date)->bool:
            """
            Comproba que no hi ha cap conflicte de solapament amb la data, pacient i doctor.
            
            :param start_date: data d'inici cita en format YYYY-MM-DD (ISO)
            :param end_date: data d'inici cita en format YYYY-MM-DD (ISO)
            :return: Si no hi ha conflicte(True) o si hi ha o algun altre problema(False)
            :rtype: bool
            """

            # comprobo que no hi hay conflicte de dates

            #   agenda:      start |-------------------| end
            #   proposta:               start |------------------|end -> falla
            #   proposta: start|-----------|end -> falla
        
            try:
                # comprobo que cap cita te data inici entre START i END nova cita
                stmt = db.select(Appointment).where(db.between(Appointment.c.dt_start,start_date, end_date).dt_start).where(Appointment.c.id_doctor)
                entity = db.session.execute(stmt).fetchone()
                if entity:
                    return False
                
                # comprobo que cap cita te data inici entre START i END nova cita
                stmt = db.select(Appointment).where(db.between(Appointment.c.dt_start,start_date, end_date).dt_start)
                entity = db.session.execute(stmt).fetchone()
                if entity:
                    return False
                
            except:
                # algun problema amb la consulta base de dades
                return False
            
            # no hi ha conflictes
            return True
            


        try:
            data = request.json
            new_app = Appointment()
            
            if not new_app.from_json(data):
                return json_error(HTTP_ERROR(HTTP_400_BAD_REQUEST))

            # miro que no hi hagi cap col·lisió amb cites i
            # que tant el doctor, centre o pacient existeixen i estan actius
            if check_entity('patient',new_app.id_patient) and \
                check_entity('doctor', new_app.id_doctor) and \
                check_entity('clinic', new_app.id_clinic):

                if not check_conflicts(new_app.id_doctor, new_app.id_patient,new_app.dt_start,new_app.dt_end):
                    # afexeixo el nou appointment
                    db.session.add(new_app)
                    return jsonify(new_app),HTTPStatus.OK
        except:


        return jsonify({})
            appointment = Appointment()

    @app.route('/<int:id>', methods=['PUT'])
    def modify_appointment(id:int):
        try:
            appointment:Appointment = db.session.get(Appointment,id)
            if not appointment:
                return json_error(HTTP_ERROR(HTTP_404_NOT_FOUND))
            
            data = request.json
            new_date = data.get('date')
            new_start_time = data.get('start')
            new_end_time = data.get('end')
            new_doctor_id = data.get('doctor_id')
            

        except:
            return json_error(HTTP_ERROR(HTTP_500_INTERNAL_SERVER_ERROR))

    @app.route('/cancel/<id>', methods=['PUT'])
    def cancel_apointment(id):
        try:
            appointment:Appointment = db.session.get(Appointment,id)
            appointment.status = False
            db.session.commit()
            return jsonify(appointment.to_dict())

        except:
            return json_error(HTTP_ERROR(HTTP_204_NO_CONTENT))


    return app

if __name__ == '__main__':
    app = create_app()
    app.run(app.run(host=app.config['ADMIN_LISTEN'], port = app.config['ADMIN_PORT']))