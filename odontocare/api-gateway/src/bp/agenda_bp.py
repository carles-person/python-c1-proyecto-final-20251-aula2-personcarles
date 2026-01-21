"""
Docstring for odontocare.api-gateway.bp.agenda_bp
"""
import requests
import os
from flask import Blueprint,jsonify, current_app, request
from octools import json_error,json_message, HTTPStatus, role_required,token_required, OCROL, OCERR, OCENT


agenda_bp = Blueprint('agenda_bp',__name__)

SECRET_KEY = os.environ.get('OC_SECRET_KEY', '1234')

# health check del servei AGENDA_SVC
@agenda_bp.route('/health', methods=['GET'])
@token_required
def health():
    """
    Crida al AGENDA_SVC i fa un check the health
    """
    header = {
        'content-type': 'application/json',
    }
    try:
        response = requests.get(f'{current_app.config['OC_AGENDA_SVC']}/health', headers = header)
        return jsonify(response.json())
    except:
        return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, OCERR.ADMIN_SVC_ACCESS_ERROR)


@agenda_bp.route('/', methods = ['GET'] )
@role_required([OCROL.ADMIN, OCROL.ASSISTANT,OCROL.DOCTOR],SECRET_KEY)
def get_appointment1():
    app_date = request.args.get('date','')
    app_time = request.args.get('time','')
    doctor_id = request.args.get('doctor')
    patient_id = request.args.get('patient')

    return json_message(HTTPStatus.OK, "Not implemented yet")

@agenda_bp.route('/add', methods=['POST'])
@role_required([OCROL.ADMIN, OCROL.ASSISTANT], SECRET_KEY)
def add_appointment():
    data = request.get_json(silent=True)
    if not data:
        return json_error(HTTPStatus.BAD_REQUEST, OCERR.JSON_ERROR)
    
    token = request.headers.get('Authorization')
    
    header = {
        'content-type': "application/json",
        "Authorization": token
    }

    try:
        result = requests.post(f'{current_app.config['OC_AGENDA_SVC']}/add', headers=header, json= data)
        return jsonify(result.json()), result.status_code
    except:
        # problemes amb la comunicacion amb AGENDA_SVC
        return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, OCERR.AGENDA_SVC_ACCESS_ERROR)


@agenda_bp.route('/get', methods=['GET'])
@role_required([OCROL.ADMIN, OCROL.ASSISTANT, OCROL.DOCTOR], SECRET_KEY)
def get_appointments():
    token = request.headers.get('Authorization')
    header = {
        'content-type': "application/json",
        "Authorization": token
    }

    query_str= ''
    entity_type = request.args.get('entity','').lower()
    entity_id = request.args.get('id',0)
    date_start = request.args.get('start_date','')
    date_end = request.args.get('end_date','')
    max_results = request.args.get('maxresults',20)

    # constucció de la query string
    if entity_type !='' and entity_id !=0:
        query_str += f'entity={entity_type}&id={entity_id}&'
    if date_start !='':
        query_str += f'start_date={date_start}&'
    if date_end !='':
        query_str += f'end_date={date_end}&'
    
    query_str += f'maxresults={max_results}'

    try:
        results = requests.get(f'{current_app.config["OC_AGENDA_SVC"]}/get?{query_str}', headers=header)
        return jsonify(results.json())
    except Exception as e:
        return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, OCERR.AGENDA_SVC_ACCESS_ERROR)
    

@agenda_bp.route('/change/<int:id>', methods=['PUT'])
@role_required([OCROL.ADMIN, OCROL.ASSISTANT], SECRET_KEY)
def change_appointment(id:int):
    data = request.get_json(silent=True)
    if not data:
        return json_error(HTTPStatus.BAD_REQUEST, OCERR.JSON_ERROR)
    
    token = request.headers.get('Authorization')
    
    header = {
        'content-type': "application/json",
        "Authorization": token
    }
    
    body = request.get_json(silent=True)
    if not body:
        return json_error(HTTPStatus.BAD_REQUEST, OCERR.JSON_ERROR)

    try:
        return jsonify(requests.put(f'{current_app.config['OC_AGENDA_SVC']}/change/{id}', headers=header, data= body).json())
    except:
        # problemes amb la comunicacion amb AGENDA_SVC
        return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, OCERR.AGENDA_SVC_ACCESS_ERROR)


@agenda_bp.route('/cancel/<int:id>', methods=['PUT'])
@role_required([OCROL.ADMIN, OCROL.ASSISTANT], SECRET_KEY)
def cancel_appointment(id:int):
    token = request.headers.get('Authorization')
    
    header = {
        'content-type': "application/json",
        "Authorization": token
    }

    try:
        result = requests.put(f'{current_app.config["OC_AGENDA_SVC"]}/cancel/{id}', headers=header)
        return jsonify(result.json())
    except:
        # problemes amb la comunicacion amb AGENDA_SVC
        return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, OCERR.AGENDA_SVC_ACCESS_ERROR)
