
from flask import request
from functools import wraps
import jwt
from tools import json_error, HTTPStatus


def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return json_error(HTTPStatus.UNAUTHORIZED,'Missing Token')
        return func(*args, **kwargs)
    return wrapper



def role_required(role_required:str,secret_key):
    def decorated_function(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return json_error(HTTPStatus.UNAUTHORIZED,'Missing Token')
            token = auth_header.split(' ')[1]
            try:
                payload = jwt.decode(token, secret_key, algorithms=['HS256'])
                role=payload.get('role','')
                if role != role_required:
                    return json_error(HTTPStatus.FORBIDDEN, f'Access denied: {role} not allowed')
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                return json_error(HTTPStatus.UNAUTHORIZED,'TOKEN is invalid or expired')
            except:
                return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, 'Internal Error projessing Token')
            
            return func(*args, **kwargs)
        return wrapper
    return decorated_function

def login_required():
    def decorated_function(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorated_function