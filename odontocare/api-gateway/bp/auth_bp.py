"""
Docstring for odontocare.api-gateway.bp.auth_bp
"""
import requests
import os
from flask import Blueprint,jsonify, current_app, request
from octools import json_error,HTTPStatus, role_required, token_required,OCROL, OCERR


auth_bp = Blueprint('auth_bp',__name__)

SECRET_KEY = os.environ.get('OC_SECRET_KEY', '1234')

# health check del servei AUTH_SVC
@auth_bp.route('/health', methods=['GET'])
@token_required
def health():
    """
    Crida al AUTH_SVC i fa un check the heald
    """
    header = {
        'content-type': 'application/json',
    }
    try:
        response = requests.get(f'{current_app.config['OC_AUTH_SVC']}/health', headers = header)
        return jsonify(response.json())
    except:
        return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, OCERR.ADMIN_SVC_ACCESS_ERROR)
    



#Endpoint per "Authentication"
@auth_bp.route('/login', methods=['POST'])
def login():
    """
        Endpoint per **/login**
        rep usuari i password en el "body" del missatge (application/json)
        :ROL : tots els usuaris
        ```
        body = {
            "username" : user_name,
            "password" : password
            }
            ```

        Returns:
            :JWT Token: retorna un token JWT en el body 
            ```
            {
                "token" : token_del usuari per ser usat en posteriors authentificacions}
            }
            ```
    """
    # obtinc les credencials,
    credentials = request.get_json(silent=True)
    # si no hi ha credencials o ni ha info JSON retorno error 415
    if not credentials:
        return json_error(HTTPStatus.BAD_REQUEST,OCERR.JSON_ERROR)
    
    username = credentials.get('username','')
    password = credentials.get('username','')

    if not username or not password:
        return json_error(HTTPStatus.BAD_REQUEST, OCERR.JSON_ERRO)
    
    # login i obtenció del Token cridant AUTH_SVC
    payload = {
        'username': username,
        'password': password
    }
    header = {
        'content-type': 'application/json'
    }
    try:
        response = requests.post(f'{current_app.config['OC_AUTH_SVC']}/login',headers=header,json=payload)
        return jsonify(response.json())
    
    except:
        return json_error(HTTPStatus.INTERNAL_SERVER_ERROR,OCERR.AUTH_SVC_ACCESS_ERROR)


@auth_bp.route('/validate/<int:id>')
@role_required(OCROL.ADMIN,SECRET_KEY)
def validate(id:int):
    """
    Funció que crida http://AUTH_SVC:port/validate/<id>

    Requereix in **TOKEN** valid per executar-se (user logged-in). Seguretaa ve implementada en el servei
    
    :param id: id usuari per validar amb el token
    :type id: int 

    :return: json message
    :rtype: json
    
    ```
    {
        "valid" : [True, False]
        "role" : [OCROL del usuari authenticat]
    }
    ```
    :HTTP Status, HTTP_OK, HTTP_500, HTTP_40X
    """

    token = request.headers.get('Authorization')
    header = {
        'content-type': 'application/json',
        'Authorization': token
    }

    # crido el microservei d'authenitificació
    try:
        response = requests.get(f'{current_app.config['OC_AUTH_SVC']}/validate/{id}',headers=header)
        return jsonify(response.json())
    except:
        return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, OCERR.AUTH_SVC_ACCESS_ERROR)
    

@auth_bp.route('/register', methods=['POST'])
@role_required(OCROL.ADMIN,SECRET_KEY)
def register():
    """
    Funció que crida http://AUTH_SVC:port/register>

    Requereix in **TOKEN** valid per executar-se (user logged-in)
    **ROL**: ve limitat pel servei
    
    :param body: id usuari per validar amb el token
    :type body: json
    ```
    body = {
          "username": user_name,
          "password": password_for_the_user,
          "role": user_role
        }
    ```


    :return: json message
    :rtype: json
    ```
        body = {
            "valid": [True o False],
            (solo si True) "role": rol}
        ```
    :returns status: HTTP_OK or HTTP_401(Unauthorized) or HTTP_500 (user adding error)
    """

    # obtinc el token
    token = request.headers.get('Authorization','')

    # obtinc el "boyd", i si es correcte també  el nou usuar, password i nol
    response = request.get_json(silent=True)
    if not response:
        return json_error(HTTPStatus.BAD_REQUEST,OCERR.JSON_ERROR)
    
    username = response.get('username','')
    password = response.get('password','')
    user_role = response.get('role','')

    # creo el header i el payload
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
        response = requests.post(f'{current_app.config['OC_AUTH_SVC']}/register',headers=header,json=payload)
        return jsonify(response.json())
    except:
        return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, OCERR.AUTH_SVC_ACCESS_ERROR)
    

@auth_bp.route('/list', methods = ['GET'])
@role_required(OCROL.ADMIN,SECRET_KEY)
def get_users():
    """
    Funció que crida `http://AUTH_SVC:port/users` . obté una llista dels usuaris del sistema
    :param header: header del http request
    :type header: json
    ```
    header = {
        ...
        "Authorization": "Bearer [TOKEN]"
        }
    ```

    :return: llista d'usuaris registrats
    :rtype: [json]
    """
    
    token = request.headers.get('Authorization')
    
    # crido al microservei d'AUTH
    header = {
        'content-type': 'application/json',
        'Authorization': token
    }

    try:
        response = requests.get(f'{current_app.config['OC_AUTH_SVC']}/users')
        return jsonify(response.json())
    
    except:
        return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, OCERR.AUTH_SVC_ACCESS_ERROR)






    