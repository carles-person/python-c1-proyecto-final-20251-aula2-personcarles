"""
Docstring for odontocare.api-gateway.bp.auth_bp
"""
import requests
from flask import Blueprint,jsonify, current_app, request
from tools import json_error,HTTPStatus, role_required, token_required,OC_ROLES, OCERR


auth_bp = Blueprint('auth_bp',__name__)


# common Checks for token


#Endpoint per "Authentication"
@auth_bp.route('/login', methods=['POST'])
def login():
    # obtinc les credencials,
    credentials = request.get_json(silent=True)
    # si no hi ha credencials o ni ha info JSON retorno error 415
    if not credentials:
        return json_error(HTTPStatus.UNSUPPORTED_MEDIA_TYPE,'NO JSON Contnt Found')
    
    username = credentials['username']
    password = credentials.password

    if not username or not password:
        return json_error(HTTPStatus.BAD_REQUEST, 'Credentials not passed correctly')
    
    # login i obtenció del Token

    payload = {
        'username': username,
        'password': password
    }
    header = {
        'content-type': 'application/json'
    }
    try:
        response = requests.post(f'{current_app.config['AUTH_SVC']}/login',headers=header,json=payload)

        #TODO: check if the response needs jsonify
        return response #
    
    except:
        return json_error(HTTPStatus.INTERNAL_SERVER_ERROR,OCERR.AUTH_SVC_ACCESS_ERROR)


@auth_bp.route('/validate/<int:id>')
@token_required
def validate(id:int):

    token = request.headers.get('Authorization')
    header = {
        'content-type': 'application/json',
        'Authorization': token
    }

    # crido el microservei d'authenitificació
    try:
        response = requests.get(f'{current_app.config['AUTH_SVC']}/validate/{id}',headers=header)
        return response
    except:
        return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, OCERR.AUTH_SVC_ACCESS_ERROR)
    

@auth_bp.route('/register', methods=['POST'])
@role_required(OC_ROLES.ADMIN)
def register():

    # oting el token
    token = request.headers.get('Authorization')

    # obtinc el nou usuari i password
    response = request.get_json()
    username = response.get('username')
    password = response.get('password')
    user_role = response.get('role')

    header = {
        'content-type': 'application/json',
        'Authorization': token
    }

    payload = {
        'username': username,
        'password': password,
        'role': user_role
    }

    # crido microservei d'authentificació /per registre
    try:
        response = requests.get(f'{current_app.config['AUTH_SVC']}/register',headers=header,json=payload)
        return response
    except:
        return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, OCERR.AUTH_SVC_ACCESS_ERROR)
    

@auth_bp.route('/users', methods = ['GET'])
@role_required(OC_ROLES.ADMIN)
def get_users():
    
    token = request.headers.get('Authorization')
    
    # crido al microservei d'AUTH
    header = {
        'content-type': 'application/json',
        'Authorization': token
    }

    try:
        response = requests.get(f'{current_app.config['AUTH_SVC']}/list',  headers=header)
        return response
    
    except:
        return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, OCERR.AUTH_SVC_ACCESS_ERROR)






    