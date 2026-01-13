
                
import os
import sys
from flask import Flask, request, jsonify
import requests
from http import HTTPStatus

from models import Clinic, Patient, Doctor,db

from tools import OCERR, OCENT,OCROL, role_required, json_error, json_message

def create_app():
    app = Flask(__name__)
    # configuro les variables
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///admin.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('OC_SECRET_KEY', 'development_secret')
    app.config['ADMIN_LISTEN_HOST'] = os.environ.get('ADMIN_LISTEN_HOST', '0.0.0.0')
    app.config['ADMIN_LISTEN_PORT'] = os.environ.get('ADMIN_LISTEN_PORT', 4002)
    app.config['OC_AUTH_SVC'] = os.environ.get('OC_AUTH_SVC','http://localhost:4001')
    # Creo les taules a la BD
    db.init_app(app)
    with app.app_context():
        db.create_all()

    """ 
    Defineixo els endpoints per cada un dels microserveis:
    - creacio d'un usuari i/o modificació
    - creació i modificacio un metge
    - creació i modificació d'un pacient
    - creació i modificació d'una clinica o centre
    -
    """

    # defineixo una funcio per crear qualsevol tipus d'usuari
    def create_auth_user(username, password, role):
        try:
            resp = requests.post(f'{app.config['OC_AUTH_SVC']}/register', json={
                'username': username,
                'password': password,
                'role': role
            })
            return resp.json().get('id') if resp.status_code == 201 else None
        except:
            return None  

    # POST /doctor: creació doctor o comprobació
    
    @app.route('/doctor', methods=['POST','GET'])
    def doctor():
        data=request.get_json()

        # creació un usuari tipus DOC
        user_id = create_auth_user(data['username'],data['password'],OCROL.DOCTOR)

        if not user_id:
            return json_error(HTTPStatus.SERVICE_UNAVAILABLE,'Not Possible to connect to AUTH_SVC')
        try:
            new_doctor = Doctor(id_user=user_id, name=data['name'], speciality=data['speciality'] )
            db.session.add(new_doctor)
            db.session.commit()

            return json_message(HTTPStatus.CREATED, f'Doctor created with id:{new_doctor.id}')
        except Exception as e:
            return json_error(HTTPStatus.BAD_REQUEST,OCERR.ENTITY_REGISTRATION_ERROR)     

    @app.route('/patient', methods=['POST','GET'])
    def patient():
        data= request.get_json()
        # creació un usuari tipus DOC
        user_id = create_auth_user(data['username'],data['password'], OCROL.PATIENT)
        if not user_id:
            return json_error(HTTPStatus.SERVICE_UNAVAILABLE,'Not Possible to connect to AUTH_SVC')
        try:
            new_patient = Patient(id_user=user_id, name=data['name'], phone=data['phone'],status=True)
            db.session.add(new_patient)
            db.session.commit()
            return json_message(HTTPStatus.CREATED,f'Patient created with id:{new_patient.id}')
        except:
            return json_error(HTTPStatus.BAD_REQUEST,OCERR.ENTITY_REGISTRATION_ERROR)  
        
    @app.route('/clinic', methods=['POST','GET'])
    def clinic():

        data = request.get_json()
       
       # creació una entitat clinica
        try:
            new_clinic = Clinic(name=data['name'], address=data['address'],status=True)
            db.session.add(new_clinic)
            db.session.commit()
            return json_message(HTTPStatus.CREATED,f'Clinic created with id:{new_clinic.id}')
        except:
            return json_error(HTTPStatus.BAD_REQUEST,OCERR.ENTITY_REGISTRATION_ERROR)  
        
    # GET /check?entity=&id= : end point comproba existencia doctor, clinica o pacient i el seu estat
    @app.route('/check', methods = ['GET'])
    def check_exists():
        entity_type = request.args.get('entity','').lower()
        entity_id = int(request.args.get('id',0))

        if entity_type == '' or entity_id <0:
            return jsonify({'error': f'Entity or entitity id is not given'}), HTTPStatus.BAD_REQUEST
        
        if entity_type == OCENT.DOC:
            entity = db.session(db.select(Doctor,entity_id)).scalar_one()
        elif entity_type == OCENT.PATIENT:
            entity = db.session(db.select(Patient,entity_id)).scalar_one()
        elif entity_type == OCENT.CLINIC:
            entity = db.session(db.select(Clinic,entity_id)).scalar_one()
        else:
            return json_error(HTTPStatus.BAD_REQUEST, OCERR.ENTITY_IS_WRONG)
        
        if not entity:
            msg = {'message': f'{entity_type.upper()} not found', 'status': 0}
            http_code = HTTPStatus.NOT_FOUND
        else:
            msg={'message': f'{entity_type.upper()} with {entity_id} exists', 'status': entity.status}
            http_code = HTTPStatus.OK
        
        return jsonify(msg), http_code

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(app.run(host=app.config['ADMIN_LISTEN_HOST'], port = app.config['ADMIN_LISTEN_PORT']))