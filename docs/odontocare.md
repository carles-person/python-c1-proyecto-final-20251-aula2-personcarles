# ODONTOCARE API Doc
# Introducció
## Tipus i Format de dades
Totes les capceleres tenen per defecte la següent configuració, tant en un `GET`, `POST`o `PUT`
```json
header = {
	...
	"Content-Type": "application/json"
	...
	}
```

En el cas el tipus d'operació requereixi authenticació, aleshores necessitarem afegir un _**JWT-TOKEN**_ a dita capçalera.
```json
header = {
	...
	"Authorization": "Bearer [TOKEN]"
	...
	}
```

Seguidament passem a descriure la API pública


## Public API Endpoints


_**Comon Public {API_BASE} endpoint**_ :
- **Endpoint**: `{API_BASE} = /api/v1` 

---
---
---


### PUBLIC API Auth
----

#### _**HEALTH**_: **Method**: `GET`

- **Endpoint**: `{API_BASE}/users/health`
- **Header**: amb _"Authorization"_
- **Rol**: Any
**Return**: 
```json
response =
	{
	"message": "OK: [service] System Online
	}
```

---

#### _**LOGIN*_: **Method**: `POST`
- **Endpoint**: `{API_BASE}/users/login`
- **Header**: amb _"Authorization"_
- **Rol**: Any
**Return**: 
```json
response =
	{
	"message": "OK: [service] System Online
	}
```

---

#### _**VALIDATE**_: **Method**: `GET`
- **Endpoint**: `{API_BASE}/users/validate/{id}`
- **Header**: amb _"Authorization"_
- **Rol**: ADMIN
**Return**: 
```json
response =
	{
        "valid" : [True, False],
        "role" : [OCROL del usuari authenticat]
    }
```

---
#### _**REGISTER**_: **Method**: `POST`
- **Endpoint**: `{API_BASE}/users/register`
- **Header**: amb _"Authorization"_
- **Rol**: ADMIN
- **json data in body
```json
body = {
          "username": user_name,
          "password": password_for_the_user,
          "role": user_role
        }
```
**Return**
```json
response = {
        "token" : token_del_per ser usat en posteriors authentificacions}
    	}
```
----

#### _**CHANGE PASSWORD**_: **Method**: `PUT`
- **Endpoint**: `{API_BASE}/users/newpassword`
- **Header**: amb _"Authorization"_
- **Rol**: ADMIN
- **json data in body
```json
body = {
        'new_password': new_password
    }
```
**Return**
```json
response = {
        "message" : Password Usuari {user_id}:{user.username} ha canviat correctament'}
    	}
```
---
_**LIST**_: **Method**: `GET`
- **Endpoint**: `{API_BASE}/users/list`
- **Header**: amb _"Authorization"_
- **Rol**: ADMIN
- **json data in body**
```json
body = {
          "username": user_name,
          "password": password_for_the_user,
          "role": user_role
        }
```
**Return**
```json
response = [
		{'id': self.id, 'username': self.username, 'role': self.role }
]
```
----
----
----


### PUBLIC API Admin
#### _**HEALTH**_: **Method**: `GET`

- **Endpoint**: `{API_BASE}/admin/health`
- **Header**: amb _"Authorization"_
- **Rol**: Any
**Return**: 
```json
response =
	{
	"message": "OK: [service] System Online
	}
```
----

#### _**CHECK**_: **Method**: `GET`

- **Endpoint**: `{API_BASE}/admin/check?entity={type}&id={id}`
- **Header**: amb _"Authorization"_
- **Rol**:: ADMIN
- **Parameters**:
	- entity = 'patient','doctor','clinic
**Return**: 
`HTTP_20X` or `HTTP_40X` or `HTTP_50X`
```json
response =
	{
		"message": f'{entity_type.upper()} with {entity_id} exists',
		"status": entity.status // [True or False] (si esta actiu o no)
	}
```
----

#### _**LIST**_: **Method**: `GET`

- **Endpoint**: `{API_BASE}/admin/list/{entity}`
- **Header**: amb _"Authorization"_
- **Rol**:: ADMIN
- **{entity}**: 'patient','doctor','clinic

**Return**: 
`HTTP_20X` or `HTTP_40X` or `HTTP_50X`
```json
response = [
	{ "{entity}": {self.name} (id={self.id})(user_id={self.id_user}) }

]
```
----

#### _**ADD**_: **Method**: `POST`

- **Endpoint**: `{API_BASE}/admin/list/{entity}`
- **Header**: amb _"Authorization"_
- **Rol**:: ADMIN
- **Body**:
	```json
	body = { 
            "entity": entitat <- (doctor, pacient)
            "name": nom_de_la_entitat (doctor, patient o clinic,
            "speciality": expecialitat (<-per doctors),
            "phone": telefon (<- per pacients),
            "address"; adreça (<-per cliniques)
            "user"(opcional):  <- (nomes doctors o patients)
            {
                "username": usuari a registrar,
                "password": password_del_usuario
            }
            }
	```
**Return**: 
`HTTP_20X` or `HTTP_40X` or `HTTP_50X`
```json
response = {
	"id": new_patient.id,
	"message": f'Patient created with id:{new_patient.id}
```
----
---
---


### PUBLIC API Agenda
#### _**HEALTH**_: **Method**: `GET`

- **Endpoint**: `{API_BASE}/agenda/health`
- **Header**: amb _"Authorization"_
- **Rol**: Any

**Return**: 
`HTTP_20X` or `HTTP_40X` or `HTTP_50X`
```json
response =
	{
	"message": "OK: [service] System Online
	}
```
----

#### _**ADD**_: **Method**: `POST`

- **Endpoint**: `{API_BASE}/agenda/add`
- **Header**: amb _"Authorization"_
- **Rol**: ADMIN, ASSISTTANT
- **Body**:
```json
body = {
	// sistem rounds up to 15 minutes slots
	"date": "2025-01-01", 	// date in ISO format
	"time": "11:45", 		// time in ISO format
	"duration": 30,			//minutes
	"patient_id": {id},		// id from patient table
	"doctor_id": {id},		// id from doctor table
	"clinic_id": {id},		// id from clinic table
	"user_id": {id},		// id from user logged in 
	"reason": "reason of visit"
}
```

**Return**: 
`HTTP_20X` or `HTTP_40X` or `HTTP_50X`
```json
response =
	{
		"id": self.id,
		"patient_id": self.id_patient,
		"reason": self.reason,
		"date": self.dt_start.date().isoformat(), 
		"duration_minutes": duration
	}
```
----

#### _**GET Appointments**_: **Method**: `GET`

- **Endpoint**: `{API_BASE}/agenda/get?entity{entity}&id={id}&start_date={start date}&end_date={end_date}&maxresults=20`
- **Header**: amb _"Authorization"_
- **Rol**: ADMIN, ASSISTTANT, DOCTOR
- **parameters**: diferents filtres
	- `entity`: dipus entitat a filtra
	- `id`: id entitat( clinic, doctor o patient)
	- `start_date`: data inici
	- `end_date`: data final
	- `maxresults`: max resultats que donara (20 per defecte)
```json
body = {
	// sistem rounds up to 15 minutes slots
	"date": "2025-01-01", 	// date in ISO format
	"time": "11:45", 		// time in ISO format
	"duration": 30,			//minutes
	"patient_id": {id},		// id from patient table
	"doctor_id": {id},		// id from doctor table
	"clinic_id": {id},		// id from clinic table
	"user_id": {id},		// id from user logged in 
	"reason": "reason of visit"
}
```

**Return**: 
```json
response = [
	{
		'id': self.id,
		'patient_id': self.id_patient,
		'reason': self.reason,
		'date': self.dt_start.date().isoformat(), 
		'duration_minutes': duration
	} ]

```
----

#### _**CHANGEAppointments**_: **Method**: `PUT`

- **Endpoint**: `{API_BASE}/agenda/change/<id>`
- **Header**: amb _"Authorization"_
- **Rol**: ADMIN, ASSISTTANT
- **\<id\>**: id de la citad

```json
body = {
	// Nova proposta data
	"date": "2025-01-01", 	// date in ISO format
	"start": "11:45", 		// time in ISO format
	"duration": 30,			//minutes
	"doctor_id": {id},		// id from doctor table
	"clinic_id": {id},		// id from clinic table
	"reason": "reason of visit"
}
```

**Return**: 
```json
response =
	{
		'id': self.id,
		'patient_id': self.id_patient,
		'reason': self.reason,
		'date': self.dt_start.date().isoformat(), 
		'duration_minutes': duration
	} 
	
```
----
