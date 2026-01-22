
"""
Docstring for carga_inicial.carga_inicial
Fitxer que carrega un fitxer CSV inicial

Aquest procediment s'ha realitzar ja en la demo, per tant s'utilitza 
aquesta mateixa funció
"""
import requests,json
import argparse

API_SVC = 'http://localhost:4000/api/v1'

def auth_login(user, password): 
    body = {
        'username': user,
        'password': password
    }
    header = {'Content-Type': 'application/json'}

    response = requests.post(f'{API_SVC}/users/login', headers=header, data=json.dumps(body))
    token = response.json().get('token', None)
    return token

def carrega_inicial(filename):

    token =auth_login('admin','admin')
    print(f'TOKEN: {token}')

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
    

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Carrega inicial del fitxer a la BBDD.')
    parser.add_argument('filename',  type=str,
                   help='fitxer que volem carregar')
    
    args = parser.parse_args()
    if args.filename=='':
        print(parser.print_help())
        exit(1)
        

    print(f'Carregand fitxer: {args.filename}')

    carrega_inicial(args. filename)