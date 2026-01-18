import requests





endpoints = {
    'health': '/health',
    'login': '/login',
    'register': '/register',
    'validate': '/validate',
    'newpassword': '/newpassword'
}

def test_login():

    header = {
        "content-type": "application/json"
    }
    body = {
        "username": "admin",
        "password": "admin"
    }

    response = requests.get('http://localhost:40