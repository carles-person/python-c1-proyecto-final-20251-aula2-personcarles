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



### API Auth

_**HEALTH**_:
**Method**: `GET`
- **Endpoint**: `/api/1/auth/health`
- **Header**: sense _"Authorization"_
- **Rol**: Any
**Return**: 
```json
body =
	{
	"message": "OK: [service] System Online
	}
```

---




### API Admin


### API Agenda
## Auth API

**Method**: `GET`
**

# Auth Service

## Endpoints

BA

# Admin API


```
End
/add
```

```method=POST```

```json
header = {
	"Content-Type": "application/json",
	"Authorization": "Bearer XXXXXXXXXXXXXXXXXXXXXXX"
```

```json
body = {
	"entity": [ "doctor" | "clinic" | "patient" ] ,
	// siguientes campos dependerán del tipo de entidad a creat
	"name": "nom entitat: doctor pacient o clínica",
	"address"	
}
```



| ```/add```   |                                                                                                                    |
| ------------ | ------------------------------------------------------------------------------------------------------------------ |
| ```header``` | ```Content-Type: application/json```                                                                               |
| ```body```   | ```json<brHeader: {<br>Content-Type = application/json,<br>Authorization = "Bearer XXXXXXXXXXXXXXXXXXXXXXX"<br>``` |
