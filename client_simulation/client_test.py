372import requests
import json
import time as t
import random as r
import datetime as dt
import random as rdm

from modules import *

def step_04():
    print(OCT.STEP04)
    token = auth_login('admin','admin')
    print(f'TOKEN: {token}')
    return token

def step_05(token):
    print(OCT.STEP05)
    print(auth_check_svc(''))
    print(admin_check_svc(''))
    print(agenda_check_svc(''))

def step_06(token):
    print(OCT.STEP06)
    print('----> Canvi password a 12345')
    print(auth_change_password(token,'12345'))

def step_07(token):
    print(OCT.STEP07)
    filename = r'./ocdata.csv'
    r = admin_reg_users(token, filename)
    print(f'Afegits: {len(r)} nous registrer\n{r}')

def step_08(token):
    print(OCT.STEP08)
    # usuaris
    for i in range(10,110):
        new_entity={}
        new_entity['name']= f'Mr. Pacient n{i:03}'
        new_entity['phone'] = f'{i:02}-{i+3:03}-{i+6:04}'
        new_entity['role'] = 'patient'
        new_entity['entity'] = 'patient'
        a= rdm.randint(0,9)
        if a>7:
            new_entity['user'] = {
                'username': f'user_{i}',
                'password': '1234'
            }
        print(admin_reg_entity(token,new_entity))
        
    # doctors
    for i in range(10,30):
        new_entity={}
        new_entity['name']= f'Mr. Pacient n{i:03}'
        speciality = rdm.randint(0,5)
        new_entity['speciality'] = f'Speciality-{speciality:02}'
        new_entity['role'] = 'doctor'
        new_entity['entity'] = 'doctor'
        a= rdm.randint(0,9)
        if a>7:
            new_entity['user'] = {
                'username': f'user_{i}',
                'password': '1234'
            }
        print(admin_reg_entity(token,new_entity))

    #cliniques
    for i in range(10,20):
        new_entity={}
        new_entity['name']= f'SuperClinica-{i:03}'
        address = rdm.randint(0,5)
        new_entity['address'] = f'C/ Street-{address:02}, The City'
        new_entity['entity'] = 'clinic'
        print(admin_reg_entity(token,new_entity))

def step_09(token):
    print(OCT.STEP09)
    print('--> Obtinc Llista doctors metges i cliniques')

    llista_doctors = admin_get_doctor_list(token)
    llista_pacients = admin_get_patients_list(token)
    llista_cliniques = admin_get_clinics_list(token)

    print('-----> creo visita 2027-04-05@15:00 i 30min')
    response = agenda_new_appointment(token, llista_doctors[0].get('id',None),llista_pacients[1].get('id',None),llista_cliniques[1].get('id',None),
                                      "2027-04-05",'15:00', 30, "Visita 1")
    print(response)

    print('-----> creo visita amb conflicte 2027-04-05@14:30 i 45min')
    response = agenda_new_appointment(token, llista_doctors[1].get('id',None),llista_pacients[1].get('id',None),llista_cliniques[1].get('id',None),
                                      "2027-04-05",'15:00', 30, "Visita Conflicte")
    print(response)

def step_10(token):
    print(OCT.STEP10)
    llista_doctors = admin_get_doctor_list(token)
    llista_pacients = admin_get_patients_list(token)
    llista_cliniques = admin_get_clinics_list(token)
    if len(llista_cliniques)>0 and len(llista_doctors)>0 and len(llista_pacients)>0:
        for i in range(0,1000):
        
            a =rdm.randint(0,len(llista_doctors)-1)
            doctor_id = llista_doctors[a].get('id', None)

            a = rdm.randint(0,len(llista_pacients)-1)
            patient_id = llista_pacients[a].get('id', None)

            a= rdm.randint(0,len(llista_cliniques)-1)
            clinic_id = llista_cliniques[a].get('id', None)

            dt_base = dt.datetime(2026,5,1,9,0)
            dt_start = dt_base + dt.timedelta(days = r.randint(0,100), minutes = r.randint(0,600))
            duration = r.randint(0,90)
            response = agenda_new_appointment(token, doctor_id, patient_id, clinic_id,
                                        dt_start.date().isoformat(), dt_start.time().isoformat(), duration , f'---RANDOM VISITA {i:04} ---')
            print(response)

def step_11():
    print(OCT.STEP11)
    new_token = auth_login('assis_1', 'assist')
    print(f'TOKEN: {token}')
    return new_token

def step_12(token):
    print(OCT.STEP12)
    llista_doctors = admin_get_doctor_list(token)
    print(llista_doctors)
    print(f'----> un assistent, no pot obtenir llista doctors: {llista_doctors}')
    print(f'----> I al intendar fer una cita random:\n{agenda_new_appointment(token, 1,1,1, "2028-05-01", "12:00", 43, "--random")}')

def step_13(token):
    print(OCT.STEP13)
    llista_cites = agenda_get_appointments_list(token)
    print(f'----> Hi ha {len(llista_cites)} cites registrades')
    print(f'----> Anulació de 10 cites')
    for a in range(0,10):
        id =rdm.randint(0,len(llista_cites)-1)
        print(f'----> Cancel·lant cita: {id:>04}')
        agenda_cancel_appointment(token,llista_cites[id]['id'])
    print('\n----> torno a agafar llista de cites i miro quines status == False (cancel·lades)')
    llista_cites = agenda_get_appointments_list(token)
    for item in llista_cites:
        if item['status'] == False:
            print(item)

def step_14(token):
    print(OCT.STEP14)
    llista_cites = agenda_get_appointments_list_interval(token, '2026-06-05','2026-06-20')
    print(f'---> Hi ha entre 2026-06-05 i 2026-06-20 {len(llista_cites)} cites registrades')
    for item in llista_cites:
        print(item)

def step_15():
    print(OCT.STEP15)
    token = auth_login('doc_3', '1234')
    print(f'TOKEN {token}')
    return token

def step_16(token):
    print(OCT.STEP16)
    llista_cites = agenda_get_appointments_list_interval(token,'2026-06-05','2026-07-01')
    print(f'----> Amb aquest token, es poden accedir a {len(llista_cites)} cites.')
    for item in llista_cites:
        print(item)

if __name__ == "__main__":
    print('\n'*100)
    print(OCT.TITLE)
    t.sleep(1)
    SLEEP_TIME = 4
    # 04. login admin/admin
    token = step_04()
    t.sleep(SLEEP_TIME)
    
    # 05.lhealth check
    step_05(token)
    t.sleep(SLEEP_TIME)

    # 06. Canvi password
    step_06(token)
    t.sleep(SLEEP_TIME)

    # 07. Importar usuaris, cliniques, doctors
    step_07(token)
    t.sleep(SLEEP_TIME)

    # 08. Afegir (random, usuaris, doctors)
    step_08(token)
    t.sleep(SLEEP_TIME)

    # 09 Afegir cita i cita conflictiva
    step_09(token)
    t.sleep(SLEEP_TIME)

    # 10. Afegir 1000 cites Random
    step_10(token)
    t.sleep(SLEEP_TIME)

    # 11. Canviar a usuari assistent
    token2 = step_11()
    t.sleep(SLEEP_TIME)

    # 12. Error en afegit nova cita (permis)
    step_12(token2)
    t.sleep(SLEEP_TIME)

    # 13. prova anul·lació cites
    step_13(token2)
    t.sleep(SLEEP_TIME)

    # 14. Filtre cites varis
    step_14(token2)
    t.sleep(SLEEP_TIME)
    
    # 15. Login Metge
    token_metge = step_15()
    t.sleep(SLEEP_TIME)

    # 16. Prova consulta agenda
    step_16(token_metge)

    print(OCT.FINAL)





          



