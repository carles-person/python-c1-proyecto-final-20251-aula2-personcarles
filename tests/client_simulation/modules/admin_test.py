import requests
import json
from modules import API_SVC

def admin_check_svc(token):
    header = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    response = requests.get(f'{API_SVC}/admin/health', headers=header)
    return response.json()

def admin_reg_users(token, filename):
    header = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

    responses = []
    with open(filename, 'r') as f:
        for entry in f.readlines()[1:]:
            body = {}
            print('Registering:', entry.strip())
            items = entry.strip().split(',')

            entity = items[0].lower()
            body['entity'] = entity
            if entity in ['admin', 'assistant']:
                body['username'] = items[1]
                body['password'] = items[2]
                body['role'] = entity
                responses.append( requests.post(f'{API_SVC}/users/register', headers=header, data=json.dumps(body)).json())

            elif entity in ['doctor', 'patient', 'clinic']:
                body['name'] = items[1]
                if entity == 'clinic':
                    body['address'] = items[2]
                elif entity == 'patient':
                    body['phone'] = items[2]
                elif entity == 'doctor':
                    body['speciality'] = items[2]
                if len(items) > 3 and items[3]: # tinc username i password
                    body['user'] = {'username': items[3], 'password': items[4] }

                result = requests.post(f'{API_SVC}/admin/add', headers=header, data=json.dumps(body))
                responses.append(result.json())
                print('Response:', result.json())
        return responses

def admin_reg_entity(token, entity):
    header = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

    body = json.dumps(entity)
    response = requests.post(f'{API_SVC}/admin/add', headers=header, data=body)
    return response.json()
    

def admin_get_doctor_list(token):
    header = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    response = requests.get(f'{API_SVC}/admin/list/doctor', headers=header)
    return response.json()

def admin_get_patients_list(token):
    header = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    response = requests.get(f'{API_SVC}/admin/list/patient', headers=header)
    return response.json()

def admin_get_clinics_list(token):
    header = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    response = requests.get(f'{API_SVC}/admin/list/clinic', headers=header)
    return response.json()

