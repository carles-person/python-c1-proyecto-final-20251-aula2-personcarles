
                
import os
import sys
from flask import Flask, request, jsonify
import requests
from http import HTTPStatus

from models import Clinic, Patient, Doctor,db

from octools import OCERR, OCENT,OCROL, role_required, token_required, json_error, json_message

def create_app():
    app = Flask(__name__)
    # configuro les variables
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('ADMIN_DATABASE_URI', 'sqlite:///admin.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('OC_SECRET_KEY', '1234')
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
    def create_auth_user(username, password, role, header=''):
        try:
            body= {
                'username': username,
                'password': password,
                'role': role
            }

            resp = requests.post(f'{app.config['OC_AUTH_SVC']}/register', headers= header,json={
                'username': username,
                'password': password,
                'role': role
            })
            return resp.json().get('id')
        except:
            return False 
        
    # GET /health
    @app.route('/health', methods=['GET'])
    def health():
        """
        Funcio per comprobar l'estat del servei
        retorna un missatge amb "OK"
        """
        return json_message(HTTPStatus.OK, 'OK: ADMIN_SVC System Online')

    # POST /doctor: creació doctor o comprobació
    @app.route('/doctor', methods=['POST'])
    @token_required
    def doctor():
        """
        Endpoint per registrar un doctor. Si a més, es passa usuario/contraseña
        També registra un nou usuari
        
        :HTTP REQUEST:
        ```
        header = {
          ...
          "Authorization": "Bearer [el token de usuario fa sol·licitud]}
        }
        body = { //para DOCTOR
          "name": nom_del_doctor,
          "speciality": expecialitat_del_doctor,
          "user"(opcional): 
            {
              "username": usuari a registrar,
              "password": password_del_usuario
            }
          }
        ```    
        :returns json message: 
        ```
        body = {
            "valid": [True o False],
            (solo si True) "role": rol}
        ```
        :returns status: HTTP_OK, HPPT_400 (no json inforecieved), HTTP_401(Unauthorized) or HTTP_50X (problems with DB)
        """
        data=request.get_json(silent=True)
        
        if data is None:
            return json_error(HTTPStatus.BAD_REQUEST, OCERR.JSON_ERROR)
        
        # creació un usuari tipus DOC (si es vol tenir un usuari)
        # obtinc les dades del usuari/password

        new_user_data = data.get('user',None)

        if new_user_data and new_user_data['username'] and new_user_data['password']:

            user_id = create_auth_user(new_user_data['username'],new_user_data['password'],OCROL.DOCTOR,request.headers)
            if not user_id:
                return json_error(HTTPStatus.SERVICE_UNAVAILABLE,OCERR.AUTH_SVC_ACCESS_ERROR)
            
        # Creo una nova entitat  "DOCTOR"
        try:
            new_doctor = Doctor(name=data['name'], speciality=data['speciality'] )
            if new_user_data:
                new_doctor.id_user = user_id
            db.session.add(new_doctor)
            db.session.commit()

            return jsonify({'id': new_doctor.id, 'message': f'Doctor created with id:{new_doctor.id}'}), HTTPStatus.CREATED
                           
        except Exception as e:
            return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, OCERR.ENTITY_REGISTRATION_ERROR)     

    # POST /patient: creació pacient o comprobació
    @app.route('/patient', methods=['POST'])
    @token_required
    def patient():
        """
        Endpoint per registrar un pacient. si passem usuari/password,
        també crea registra un nou usuari
        
        :ROL: "ADMIN"
        :HTTP REQUEST:
        ```
        header = {
          ...
          "Authorization": "Bearer [el token de usuario fa sol·licitud]}
        }
        body = { //para DOCTOR
          "name": nombre_del_doctor,
          "speciality": expecialidad_del_doctor,
          "user"(opcional): 
            {
              "username": usuario a registrar,
              "password": password_del_usuario
            }
          }
        ```    
        :returns json message: 
        ```
        body = {
            "valid": [True o False],
            (solo si True) "role": rol}
        ```
        :returns status: HTTP_OK, HPPT_400 (no json inforecieved), HTTP_401(Unauthorized) or HTTP_50X (problems with DB)
        """

        # agafo dades JSON, si fallo torno amb Error
        data=request.get_json(silent=True)
        if data is None:
            return json_error(HTTPStatus.BAD_REQUEST, OCERR.JSON_ERROR)
        
        # creació un usuari tipus PACIENT (si es vol tenir un usuari)
        # obtinc les dades del usuari/password i creo usuari
        new_user_data = data.get('user',None)

        if new_user_data and new_user_data['username'] and new_user_data['password']:
            user_id = create_auth_user(new_user_data['username'],new_user_data['password'],OCROL.PATIENT,request.headers)
            if not user_id:
                return json_error(HTTPStatus.SERVICE_UNAVAILABLE,OCERR.AUTH_SVC_ACCESS_ERROR)
            
        # Creo una Entitat PACIENT
        try:
            new_patient = Patient(name=data['name'], phone=data['phone'],status=True)
            if new_user_data:
                new_patient.id_user = user_id
            db.session.add(new_patient)
            db.session.commit()
            return jsonify({'id': new_patient.id,'message': f'Patient created with id:{new_patient.id}'}), HTTPStatus.CREATED
        except:
            return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, OCERR.ENTITY_REGISTRATION_ERROR) 

    # POST /clinic: creació clínica    
    @app.route('/clinic', methods=['POST'])
    @token_required
    def clinic():
        """
        Endpoint per registrar una clínica. 
        
        :ROL: "ADMIN"
        :HTTP REQUEST:
        ```
        header = {
          ...
          "Authorization": "Bearer [el token de usuario fa sol·licitud]}
        }
        body = { //para DOCTOR
          "name": nombre_clinica,
          "address": adress_clinica,
          }
        ```    
        :returns json message: 
        ```
        body = {
            "valid": [True o False],
            (solo si True) "role": rol}
        ```
        :returns status: HTTP_OK, HPPT_400 (no json inforecieved), HTTP_401(Unauthorized) or HTTP_50X (problems with DB)
        """

        data = request.get_json()
       
       # creació una entitat clinica
        try:
            new_clinic = Clinic(name=data['name'], address=data['address'],status=True)
            db.session.add(new_clinic)
            db.session.commit()
            return jsonify({'id': new_clinic.id, 'message': f'Clinic created with id:{new_clinic.id}'}), HTTPStatus.CREATED
        except:
            return json_error(HTTPStatus.BAD_REQUEST,OCERR.ENTITY_REGISTRATION_ERROR)  
        
    # GET /check?entity={a}&id={b} : end point comproba existencia doctor, clinica o pacient i el seu estat
    @app.route('/check', methods = ['GET'])
    @token_required
    def check_exists():
        """
        Endpoint per comprobar si una entitat existeix i si esta activa.
        
        :ROL: QUALSEVOL
        :HTTP REQUEST: ```GET: http://server:port/5000/check?entity={type}id={id}```
        ```
        header = {
          ...
          "Authorization": "Bearer [el token de usuario fa sol·licitud]}
        }
        ```    
        :returns json message: 
        ```
        body = {
            "message": Missatge_relacionat amb entitat
            "Status": [True or False] (si esta actiu o no)
            }
        ```
        :returns status: HTTP_OK, HPPT_400 (bad request), HTTP_404(Not Found) or HTTP_50X (problems with DB)
        """
        entity_type = request.args.get('entity','').lower()
        entity_id = int(request.args.get('id',0))

        if entity_type == '' or entity_id <1:
            return jsonify({'error': f'Entity type or entitity id is not given'}), HTTPStatus.BAD_REQUEST
        try:
            # catch qualsevol error amb les bbdd
            if entity_type == OCENT.DOCTOR:
                stmt=db.select(Doctor).where(Doctor.id == entity_id)
            elif entity_type == OCENT.PATIENT:
                stmt = db.select(Patient).where(Patient.id ==entity_id)
            elif entity_type == OCENT.CLINIC:
                stmt = db.select(Clinic).where(Clinic.id ==entity_id)
            else:
                return json_error(HTTPStatus.BAD_REQUEST, OCERR.ENTITY_IS_WRONG)
            entity = db.session.execute(statement=stmt).scalar_one_or_none()
        except Exception as e:
            return json_error(HTTPStatus.BAD_REQUEST, OCERR.ENTITY_IS_WRONG)
        
        if not entity:
            msg = {'message': f'{entity_type.upper()} not found', 'status': 0}
            http_code = HTTPStatus.NOT_FOUND
        else:
            msg={'message': f'{entity_type.upper()} with {entity_id} exists', 'status': entity.status}
            if entity_type != OCENT.CLINIC:
                msg['user_id'] = entity.id_user
            http_code = HTTPStatus.OK

        return jsonify(msg), http_code
    
    # GET /{entity} : llista entitats
    @app.route('/list/<string:entity>', methods=['GET'])
    @token_required
    def get_entities(entity:str):
        """
        Docstring for get_entities
        
        :param entity: Description
        :type entity: str
        """

        if entity == OCENT.CLINIC:
            stmt = db.select(Clinic)
        elif entity == OCENT.DOCTOR:
            stmt = db.select(Doctor)
        elif entity == OCENT.PATIENT:
            stmt = db.select(Patient)
        else:
            return json_error(HTTPStatus.BAD_REQUEST, OCERR.ENTITY_IS_WRONG)
        try:
            entities_list = []
            result = db.session.execute(statement=stmt).scalars().all()
            entities_list = [ ent.to_dict() for ent in result ]
            return jsonify(entities_list), HTTPStatus.OK
        except Exception as e:
            return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, OCERR.DB_ACCESS_ERROR)
        
    # GET /{entity}/{id}
    @app.route('/list/<string:entity>/<int:entity_id>', methods=['GET'])
    @token_required
    def get_entity_by_id(entity:str, entity_id:int):
        """
        Docstring for get_entity_by_id
        
        :param entity: Description
        :type entity: str
        :param entity_id: Description
        :type entity_id: int
        """

        if entity == OCENT.CLINIC:
            stmt = db.select(Clinic).where(Clinic.id == entity_id)
        elif entity == OCENT.DOCTOR:
            stmt = db.select(Doctor).where(Doctor.id == entity_id)
        elif entity == OCENT.PATIENT:
            stmt = db.select(Patient).where(Patient.id == entity_id)
        else:
            return json_error(HTTPStatus.BAD_REQUEST, OCERR.ENTITY_IS_WRONG)
        try:
            entity_obj = db.session.execute(statement=stmt).scalar_one_or_none()
            if not entity_obj:
                return json_error(HTTPStatus.NO_CONTENT, OCERR.ENTITY_NOT_FOUND)
            return jsonify(entity_obj.to_dict()), HTTPStatus.OK
        except Exception as e:
            return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, OCERR.DB_ACCESS_ERROR)

    # GET /user/{entity}/{id}
    @app.route('/user/<string:entity>/<int:user_id>', methods=['GET'])
    @token_required
    def get_entity_by_user_id(entity:str, user_id:int):
        """
        Docstring for get_entity_by_user_id

        :param entity: Description
        :type entity: str
        :param user_id: Description
        :type user_id: int
        """

        if entity == OCENT.DOCTOR:
            stmt = db.select(Doctor).where(Doctor.id_user == user_id)
        elif entity == OCENT.PATIENT:
            stmt = db.select(Patient).where(Patient.id_user == user_id)
        else:
            return json_error(HTTPStatus.BAD_REQUEST, OCERR.ENTITY_IS_WRONG)
        try:
            entity_obj = db.session.execute(statement=stmt).scalar_one_or_none()
            if not entity_obj:
                return json_error(HTTPStatus.NO_CONTENT, OCERR.ENTITY_NOT_FOUND)
            return jsonify(entity_obj.to_dict()), HTTPStatus.OK
        except Exception as e:
            return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, OCERR.DB_ACCESS_ERROR)
    return app

if __name__ == '__main__':
    print('STARTING APP')
    app = create_app()
    print('RUNNING THE APP')
    print("DATABASE:",app.config['SQLALCHEMY_DATABASE_URI'])
    print("AUTH:",app.config['OC_AUTH_SVC'] )
    app.run(host=app.config['ADMIN_LISTEN_HOST'], 
                    port = app.config['ADMIN_LISTEN_PORT'])