"""
Docstring for odontocare.api-gateway.bp.admin_bp
"""
import requests
import os
from flask import Blueprint,jsonify, current_app, request
from octools import json_error,json_message, HTTPStatus, role_required, token_required, OCROL, OCERR, OCENT

admin_bp = Blueprint('admin_bp',__name__)

SECRET_KEY = os.environ.get('OC_SECRET_KEY', '1234')


from functools import wraps
import jwt


@admin_bp.route('/health', methods=['GET'])
@token_required
def health():
    a = current_app.config['OC_ADMIN_SVC']
    header = {
        'content-type': 'application/json',
    }
    try:
        response = requests.get(f'{current_app.config['OC_ADMIN_SVC']}/health', headers = header)
        return jsonify(response.json())
    except:
        return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, OCERR.ADMIN_SVC_ACCESS_ERROR)

@admin_bp.route('/check', methods = ['GET'])
@role_required([OCROL.ADMIN,], SECRET_KEY)
def check_entity():
    """
    Crida a la funció `GET: http://OC_ADMIN_SVC:port/check?entity={type}&id={id}` del 
    servei ADMIN i comproba existencia del ID i ENTITAT passada, i en cas que si, si aquesta
    ENTITAT esta habilitada o desabilitada (STATUS)
    """

    entity_type = request.args.get('entity','').lower()
    entity_id = request.args.get('id',0)

    header = {
        'content-type': 'application/json',
        'Authorization': request.headers.get('Authorization','')
    }

    try:
        response = requests.get(f'{current_app.config['OC_ADMIN_SVC']}/check?entity={entity_type}&id={entity_id}')
        return jsonify(response.json())
    except:
        return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, OCERR.ADMIN_SVC_ACCESS_ERROR)
    
@admin_bp.route('/list/<string:entity>', methods=['GET'])
@role_required([OCROL.ADMIN,],SECRET_KEY)
def get_entities(entity:str):
    """
        API Pública: llista metges, pacients o cliniques que existeixen el la BBDD
        
        :ROL: "ADMIN"
        :HTTP REQUEST:
        ```
        header = {
            ...
            "Authorization": "Bearer [el token de usuario fa sol·licitud]}
        }
        ```
        :returns: json message
        :rtype: json
        ```
        body = {
            "valid": [True o False],
            (solo si True) "role": rol}
        ```
        :returns status: HTTP_OK, HPPT_400 (no json inforecieved), HTTP_401(Unauthorized) or HTTP_50X (problems with DB)
        """

    header = {
        'Content-type': 'application.json',
        'Authorization': request.headers.get('Authorization','')
    }


    if entity in (OCENT.CLINIC,OCENT.DOCTOR,OCENT.PATIENT):
        url_admin = f'{current_app.config['OC_ADMIN_SVC']}/list/{entity}'
    else:
        return json_error(HTTPStatus.BAD_REQUEST, OCERR.ENTITY_IS_WRONG)

    try:
        response = requests.get(url_admin, headers=header)
        return jsonify(response.json())
    except:
        return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, OCERR.ADMIN_SVC_ACCESS_ERROR)

@admin_bp.route('/add', methods=['POST'])
@role_required([OCROL.ADMIN,], SECRET_KEY)
def create_entity():
    """
    API Pública: Crea metges, pacients o cliniques que existeixen el la BBDD

    :ROL: "ADMIN"
    ```
    header = {
        ...
        "Authorization": "Bearer [el token de usuario fa sol·licitud]}
    }
    body = { 
            "entity": entitat <- (doctor, pacient)
            "name": nom_de_la_entitat (doctor, patient o clinic,
            "speciality": expecialitat (<-per doctors),
            "phone": telefon (<- per pacients),
            "address"; adreça (<-per cliniques)
            "user"(opcional):  <- (nomes doctors o patients)
            {
                "username": usuari a registrar,
                "password": password_del_usuario
            }
            }
    ```
    :returns: json message
    :rtype: json
    ```
    body = {
        "valid": [True o False],
        (solo si True) "role": rol}
    ```
    :returns status: HTTP_OK, HPPT_400 (no json inforecieved), HTTP_401(Unauthorized) or HTTP_50X (problems with DB)
    """
    data={}
    data = request.get_json(silent=True)
    header = {
        'content-type': 'application/json',
        'Authorization': request.headers.get('Authorization','')
    }

    entity_type = data.get('entity','').lower()
    if not data or entity_type=='':
        return json_error(HTTPStatus.BAD_REQUEST, OCERR.JSON_ERROR)

    if entity_type == OCENT.CLINIC:
        url_admin = f'{current_app.config['OC_ADMIN_SVC']}/clinic'
    elif entity_type == OCENT.DOCTOR:
        url_admin = f'{current_app.config['OC_ADMIN_SVC']}/doctor'
    elif entity_type == OCENT.PATIENT:
        url_admin = f'{current_app.config['OC_ADMIN_SVC']}/patient'
    else:
        return json_error(HTTPStatus.BAD_REQUEST, OCERR.ENTITY_REGISTRATION_ERROR)

    try:
        response = requests.post(url_admin, headers= header, json=data)
        return jsonify(response.json()), response.status_code
    except:
        return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, OCERR.ADMIN_SVC_ACCESS_ERROR)
