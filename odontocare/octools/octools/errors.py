"""
Docstring for odontocare.auth-svc.tools.errors
"""
from http import HTTPStatus
from flask import jsonify

from enum import StrEnum

def json_error(status_code:HTTPStatus, error_str:str =''):

    if error_str:
        message = {'error': error_str}
    else:
        message = {'error': status_code.description}
    
    return jsonify(message), status_code.value

def json_message(status_code:HTTPStatus, msg_str:str =''):

    if msg_str:
        message = {'message': msg_str}
    else:
        message = {'message': status_code.description}
    
    return jsonify(message), status_code.value




class OCERR(StrEnum):      
    AUTH_SVC_ACCESS_ERROR = 'Failed access to AUTH_SVC'
    ADMIN_SVC_ACCESS_ERROR = 'Failed to access ADMIN_SVC'
    AGENDA_SVC_ACCESS_ERROR = 'Failed to access AGENDA_SVC'
    ENTITY_IS_WRONG = 'Wrong Entity passed'
    ENTITY_REGISTRATION_ERROR = "Failed to create an entity"
    ENTITY_NOT_FOUND = "Entity not found"
    DB_ACCESS_ERROR = "DATABASE: Prolbems accessing the database"
    NOT_FOUND = "ERROR 404: Page Not Found"
    METHOD_NOT_ALLOWED = "ERROR 405: Method Not Allowed"
    JSON_ERROR = "ERROR 400: Bad Request - JSON Error in the message Body"
    TOKEN_ERROR = "ERROR 401: Invalid Token or Missing Token"



    

