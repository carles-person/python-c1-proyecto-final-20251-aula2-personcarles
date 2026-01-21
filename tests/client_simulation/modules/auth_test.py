import requests, json
from modules import API_SVC


def auth_login(user, password): 
    body = {
        'username': user,
        'password': password
    }
    header = {'Content-Type': 'application/json'}

    response = requests.post(f'{API_SVC}/users/login', headers=header, data=json.dumps(body))
    token = response.json().get('token', None)
    return token

def auth_change_password(token, password):
    header = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    body = {
        "new_password": password
        }
    response = requests.put(f'{API_SVC}/users/newpassword', headers=header, json = body)
    return response.json()              
    
def auth_check_svc(token):
    header = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    response = requests.get(f'{API_SVC}/users/health', headers=header)
    return response.json()