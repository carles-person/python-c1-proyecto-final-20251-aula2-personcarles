import os
import datetime as dt
import jwt
from http import HTTPStatus
from flask import Flask, request, jsonify
from sqlalchemy import and_, or_
import requests
from models import Appointment
from models import db

from octools import role_required, token_required, OCENT, OCERR, OCROL, json_error,json_message

def create_app():
    app = Flask(__name__)
    # configuro les variables
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///agenda.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('OC_SECRET_KEY', '1234')
    app.config['AGENDA_LISTEN_HOST'] = os.environ.get('AGENDA_LISTEN_HOST', '0.0.0.0')
    app.config['AGENDA_LISTEN_PORT'] = os.environ.get('AGENDA_LISTEN_PORT', 4003)

    app.config['OC_AUTH_SVC'] = os.environ.get('OC_AUTH_SVC','http://localhost:4001')
    app.config['OC_ADMIN_SVC'] = os.environ.get('OC_ADMIN_SVC','http://localhost:4002')

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

    @app.route('/', methods =['GET', 'POST', 'PUT'])
    @token_required
    def default():
        """
        Default endpoint
        :Returns: Error de servei no implementat
        """
        return json_error(HTTPStatus.NOT_IMPLEMENTED)
    
    @app.route('/health', methods=['GET'])
    def health():
        """
        Funcio per comprobar l'estat del servei
        retorna un missatge amb "OK"
        """
        return json_message(HTTPStatus.OK, 'OK: AGENDA_SVC System Online')
    
    @app.route('/get', methods=['GET'])
    @token_required
    def get_agenda():
        """
        Obté les cites existents, depenent del rol, l'usuari podra veure més o menys informació
        Per això. utilitzem el token per identificar l'usuari i el seu role.

        - Administradors: poder veure i filtrar totes les entitats per dates, estat, etc
        - Assistents: consultar cites pacient filtrant dates
        - doctors: poden veure únicament les seves dates

        :ROLS: [ADMIN, ASSISTANT, DOCTOR] // usuari ha d'estar validat
        :HTTP REQUEST: 
        ```
            GET: http://server:port/get
            GET: http://server:port/get?entity={entity type}&id={id}&status={status}&date_start={date}&date_end={date}&maxresults=50
        ```
        :Returns:
        :json: valors en format JSON amb totes les cites demanades.

        """
        # extrec rol i user_id del token
        auth_str = request.headers.get('Authorization',None)
        if not auth_str:
            return json_error(HTTPStatus.BAD_REQUEST, OCERR.JSON_ERROR)
        
        token = auth_str.split(' ')[1]
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])

        id = payload.get('user_id', None)
        role = payload.get('role',None)

        if not id or not role:
            return json_error(HTTPStatus.UNAUTHORIZED, OCERR.PAYLOAD_ERROR)

        # preparo l'estatement SQL
        stmt = db.select(Appointment)

        # miro si hi ha parametres amb el que s'han buscat
        start_date = request.args.get('start_date','').lower()
        end_date = request.args.get('end_date','').lower()
        entity = request.args.get('entity','').lower()
        entity_id = int(request.args.get('id',0))
        status = request.args.get('status','').lower()
        max_results = int(request.args.get('maxresults',50))

        
        if role == OCROL.DOCTOR:
            # miro usuari id que ha creat el request, i com es doctor, busco quin user id correspon al doctor_id
            try:
                result = requests.get(f'{app.config['OC_ADMIN_SVC']}/user/{OCENT.DOCTOR}/{id}', headers = request.headers)  
                if result.status_code != HTTPStatus.OK:
                    return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, OCERR.ADMIN_SVC_ACCESS_ERROR)
            except:
                return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, OCERR.ADMIN_SVC_ACCESS_ERROR)
            
            id_user = result.json().get('id', None)
            if not id_user:
                return json_error(HTTPStatus.UNAUTHORIZED, OCERR.ENTITY_NOT_FOUND)
            

            stmt = stmt.where(Appointment.id_doctor == id_user)


        elif role == OCROL.ASSISTANT:
            
            try:
                # capturo qualsevol excepció de conversió de les dates
                if start_date:
                    new_date = dt.datetime.fromisoformat(start_date)
                    stmt = stmt.where(Appointment.dt_start >= new_date)
                if end_date:
                    new_date = dt.datetime.fromisoformat(end_date)
                    stmt = stmt.where(Appointment.dt_end <= new_date)
            except Exception as e:
                # en cas error, l'ignoro ja que no hi ha problems de seguretat
                # es fara un query total (que esta limitat a 100 registres)
                pass
    

        elif role == OCROL.ADMIN:
            try: 
                stm_ext = ''
                # capturo qualsevol excepció de conversió de les dades
                # comprobo si hi ha filtre per tipus entitat (metge o centre o pacient)
                if entity == OCENT.CLINIC and entity_id != 0:
                    stmt.where(Appointment.id_clinic==entity_id)
                elif entity == OCENT.DOCTOR:
                    stmt = stmt.where(Appointment.id_doctor == entity_id)
                elif entity == OCENT.PATIENT:
                    stmt = stmt.where(Appointment.id_doctor == entity_id)
                
                # miro si hi ha un filtre temporal
                if start_date:
                    new_date = dt.datetime.fromisoformat(start_date)
                    stmt = stmt.where(Appointment.dt_start >= new_date)
                if end_date:
                    new_date = dt.datetime.fromisoformat(end_date)
                    stmt = stmt.where(Appointment.dt_end <= new_date)
                
                # miro si hi ha un filtre per cites activades/desactivades
                if status:
                    stmt = stmt.where(Appointment.status == status)

            except:
                # en cas d'excepció, no faig res ja que la query continua
                pass
        else:
            return json_error(HTTPStatus.INTERNAL_SERVER_ERROR,OCERR.DB_ACCESS_ERROR)

        # monto statement final
        try:
            stmt = stmt.limit(max_results)
            results = db.session.execute(statement=stmt).scalars().all()
        except Exception as e:
            pass
        
        return jsonify([element.to_dict() for element in results])

        
    
    # afegeix una nova cita
    @app.route('/add', methods = ['POST'])
    @token_required
    def create_appointment():

        def check_entity(entity_type:str,entity_id:int, header)->bool:
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
                response = requests.get(f'{app.config['OC_ADMIN_SVC']}/check?entity={entity_type}&id={entity_id}',headers = header)
                response.raise_for_status()
                data = response.json()
                if data['status']:
                    return True
                else:
                    return False

            except Exception as e:
                return False


        def check_no_conflict(doctor_id, patient_id, start_date, end_date)->bool:
            """
            Comproba que no hi ha cap conflicte de solapament amb la data, pacient i doctor.
            
            :param start_date: data d'inici cita en format YYYY-MM-DD (ISO)
            :param end_date: data d'inici cita en format YYYY-MM-DD (ISO)
            :return: Si no hi ha conflicte(True) o si hi ha o algun altre problema(False)
            :rtype: bool
            """

            # comprobo que no hi hay conflicte de dates

            #   agenda:      start |************************| end
            #   proposta:               start |------------------|end -> falla
            #   proposta: start|-----------|end -> falla
            #   proposta: start|---------------------------------|end -> falla
            #   proposta:           start|-----------|end -> falla

        
            try:
                # comprobo que cap cita activa doctor/pacient data inici entre START i END nova cita
                # stmt = db.select(Appointment).where(db.between(Appointment.dt_start,start_date, end_date)) \
                #         .where(Appointment.id_doctor == doctor_id).where(Appointment.id_patient == patient_id) \
                #         .where(Appointment.status == True)
                stmt = db.select(Appointment).where(Appointment.dt_start < end_date).where(Appointment.dt_end > start_date) \
                        .where(or_(Appointment.id_doctor == doctor_id, Appointment.id_patient == patient_id)) \
                        .where(Appointment.status == True)
                print(str(stmt))
                entity = db.session.execute(stmt).fetchone()
                if entity:
                    return False

            except Exception as e:
                # algun problema amb la consulta base de dades
                return False
            
            # no hi ha conflictes
            return True
            
        try:
            data = request.get_json(silent=True)
            if not data:
                return json_error(HTTPStatus.BAD_REQUEST,OCERR.JSON_ERROR)
            new_apmnt = Appointment()
            
            if not new_apmnt.from_json(data):
                return json_error(HTTPStatus.BAD_REQUEST,OCERR.JSON_ERROR)
            # obtinc el token per veure quin usuari crea la cita
            auth_str = request.headers.get('Authorization',None)
            if not auth_str:
                return json_error(HTTPStatus.BAD_REQUEST, OCERR.JSON_ERROR)
            token = auth_str.split(' ')[1]
            try:
                payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
                user_id = payload.get('user_id', None)
            except:
                return json_error(HTTPStatus.UNAUTHORIZED, OCERR.TOKEN_ERROR)

            # miro que no hi hagi cap col·lisió amb cites i
            # que tant el doctor, centre o pacient existeixen i estan actius
            header = request.headers
            if check_entity('patient',new_apmnt.id_patient, header) and \
                check_entity('doctor', new_apmnt.id_doctor, header) :
                # and  check_entity('clinic', new_apmnt.id_clinic, header):

                if check_no_conflict(new_apmnt.id_doctor, new_apmnt.id_patient,new_apmnt.dt_start,new_apmnt.dt_end):
                    # afexeixo el nou appointment
                    user_id = payload.get('user_id', None)
                    new_apmnt.id_user = user_id
                    new_apmnt.status = True
                    db.session.add(new_apmnt)
                    db.session.commit()
                    return jsonify(new_apmnt.to_dict()),HTTPStatus.CREATED
            
        except Exception as e:
            pass

        msg= dict()
        msg['message'] = 'NOK: Agenda Conflict Detected'
        msg['content'] = new_apmnt.to_dict()
        return jsonify(msg), HTTPStatus.OK

    @app.route('/change/<int:id>', methods=['PUT'])
    def modify_appointment(id:int):
        try:
            appointment:Appointment = db.session.get(Appointment,id)
            if not appointment:
                return json_error(HTTP_ERROR(HTTP_404_NOT_FOUND))
            
            data = request.json
            new_date = data.get('date',None)
            new_time = data.get('start',None)
            new_duration = data.get('duration',None)
            new_doctor_id = data.get('doctor_id',None)

            appointment.id_doctor = new_doctor_id if new_doctor_id else appointment.id_doctor
            
            # miro si hi ha canvis en hora i dia per ajustar-ho
            if new_date:
                date_iso = new_date
            else:
                date_iso = appointment.dt_start.date().isoformat()
            
            if new_time:
                time_iso = new_time
            else:
                time_iso = appointment.dt_start.time().isoformat()
            
            if new_duration:
                duration_minutes = int(new_duration/15)*15  # arrodoniment a 15minuts
                if duration_minutes <15:
                    duration_minutes = 15
            else:
                duration_minutes = int((appointment.dt_end - appointment.dt_start).seconds/60)
            
            appointment.parse_datetime(date_iso, time_iso, duration_minutes)


            db.session.commit()
            return jsonify(appointment.to_dict())

        except Exception as e:
            return json_error(HTTPStatus.INTERNAL_SERVER_ERROR)

    @app.route('/cancel/<id>', methods=['PUT'])
    def cancel_apointment(id):
        try:
            appointment:Appointment = db.session.get(Appointment,id)
            appointment.status = False
            db.session.commit()
            return jsonify(appointment.to_dict())

        except:
            return json_error(HTTPStatus.NO_CONTENT)


    return app

if __name__ == '__main__':
    app = create_app()
    print("DATABASE:",app.config['SQLALCHEMY_DATABASE_URI'])
    print("AUTH:",app.config['OC_AUTH_SVC'] )
    print("ADMIN:",app.config['OC_ADMIN_SVC'] )
    app.run(app.run(host=app.config['AGENDA_LISTEN_HOST'], port = app.config['AGENDA_LISTEN_PORT']))