import requests
from modules import API_SVC

def agenda_check_svc(token):
    header = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    response = requests.get(f'{API_SVC}/agenda/health', headers=header)
    return response.json()

def agenda_new_appointment(token, doctor_id, patient_id, clinic_id, date_iso, time_iso, duration, reason):
    header = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    body = {
            'doctor_id': doctor_id,
            'patient_id': patient_id,
            'clinic_id': clinic_id,
            'date': date_iso,
            'time': time_iso,
            'duration': duration,
            'reason': reason
    }
    response = requests.post(f'{API_SVC}/agenda/add', headers=header, json=body)
    return response.json()


def agenda_get_appointments_list(token):

    header = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

    response = requests.get(f'{API_SVC}/agenda/get', headers=header)
    return response.json()

def agenda_get_appointments_list_interval(token, start_date, end_date):
    header = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    response = requests.get(f'{API_SVC}/agenda/get?startdate={start_date}&enddate={end_date}&maxresults=50', headers=header)
    return response.json()

def agenda_cancel_appointment(token, id):
    header = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    response = requests.put(f'{API_SVC}/agenda/cancel/{id}', headers=header)
    return response.json()