"""
Docstring for odontocare.auth-svc.server
"""
import os
import datetime as dt
from flask import Flask, request, jsonify
import jwt
from models import db, User
from octools import json_error, json_message ,HTTPStatus, token_required, OCERR


def create_app():
    app = Flask(__name__)
    # configuro les variables
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('AUTH_DATABASE_URI', 'sqlite:///users.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('OC_SECRET_KEY', '1234')
    app.config['AUTH_LISTEN_HOST'] = os.environ.get('AUTH_LISTEN_HOST', '0.0.0.0')
    app.config['AUTH_LISTEN_PORT'] = os.environ.get('AUTH_LISTEN_PORT', 4001)

    # encapsulo en un try-except, sota qualsevol error el microservei es para
    try:
        db.init_app(app)
       
        # creo la base de dades i les taules si no existeixen
        with app.app_context():
            db.create_all()
            
            # si la DB es inicialitzada, aleshores creo un usuari per defecte, amb rols administrador
            # username='admin', passowrd='admin'
            if not db.session.execute(db.select(User)).first():
                db.session.add(User(username = 'admin',password='admin', role='admin'))
                db.session.commit()
    except Exception as e:
        print(f'Error a AUTH_SVC:\n{e}')
        exit(1)



    @app.route('/health', methods=['GET'])
    def health():
        """
        Funcio per comprobar l'estat del servei
        retorna un missatge amb "OK"
        """
        return json_message(HTTPStatus.OK, 'OK: AUTH_SVC System Online')
    

    # POST: /login
    @app.route('/login', methods=['POST'])
    def login():
        """
        Endpoint er login **/login**
        rep usuario i password en el "body" del missatge (application/json)
        ```
        body = {
            "username" : user_name,
            "password" : password
            }
            ```

        Returns:
            :JWT Token: retorna un token JWT en el body = 
            ```
            {
                "token" : token_del_per ser usat en posteriors authentificacions}
            }
            ```
         """
        response = request.get_json(silent=True)
        username = response.get('username')
        password = response.get('password')

        # comprobo que usuari/password son corrected
        user = db.session.execute(db.Select(User).where(User.username == username, User.password == password)).scalar()
        if user:
            # si ho es genero token i retorno
            payload = {
                'user_id': user.id,
                'role': user.role,
                'iat': dt.datetime.now(dt.timezone.utc),
                'exp': dt.datetime.now(dt.timezone.utc)+dt.timedelta(minutes=300)
            }
            token = jwt.encode(payload,app.config['SECRET_KEY'], algorithm='HS256')
            return jsonify({'token': token})
        else:
            return json_error(HTTPStatus.UNAUTHORIZED,'Wrong Credentials')
        
    @app.route('/validate/<int:user_id>', methods=['GET'])
    @token_required
    def validate(user_id):
        """
        Valida un usuario con user_id.
        esta función debe ser llamada con un token válido
        ```
        header = {
            ...
            "Authorization": "Bearer [el token de usuario que valida]}
            }
            ```
        :param user_id: id del usuario a validar
        :returns json message: 
        ```
        body = {
            "valid": [True o False],
            (solo si True) "role": rol}
        ```
        :returns status: HTTP_OK or HTTP_403
        """

        try:
            stmt = db.select(User).where(User.id == user_id)
            user = db.session.execute(statement=stmt).scalar_one_or_none()
            if not user:
                return jsonify({'valid': False}), 403
            # decodifico el token, si hi ha algun error no fa res i retorno un missatge false

            return jsonify({'valid': True, 'role': user.role}), 200
        
        except Exception as e:
            pass
        return json_error(HTTPStatus.INTERNAL_SERVER_ERROR, 'Internal Error Validating User')

    @app.route('/register', methods=['POST'])
    @token_required
    def register():
        """
        Endpoint per registrar un nou usuari
        aquesta funció ha de ser cridada per un usuari tipus admin
        ```
        header = {
          ...
          "Authorization": "Bearer [el token de usuario que valida]}
        }
        ```
        : body json:
        ```
        body = {
          "username": user_name,
          "password": password_for_the_user,
          "role": user_role
        }
        ```
        
        :returns json message: 
        ```
        body = {
            "valid": [True o False],
            (solo si True) "role": rol}
        ```
        :returns status: HTTP_OK or HTTP_401(Unauthorized) or HTTP_500 (user adding)
        """
        
        data = request.get_json(silent=True)

        if data is None:
            return json_error(HTTPStatus.BAD_REQUEST,OCERR.JSON_ERROR)
        try:
            new_user = User(username=data['username'], password=data['password'], role=data['role'])
            db.session.add(new_user)
            db.session.commit()
            
        except:
            # si hi ha problemes retorno error de registre
            # al ser els camps de User obligatoris, si username, password or role estan buits, no es
            #   farà el commit.
            return json_error(HTTPStatus.INTERNAL_SERVER_ERROR,'Problems creating new Credentials')

        return jsonify({'id': new_user.id, 'username': new_user.username, 'role': new_user.role}),HTTPStatus.CREATED


    @app.route('/newpassword', methods=['PUT'])
    @token_required
    def new_password(): 
        """
        Endpoint para que un usuario registrado cambie el password
        esta función debe ser llamada con un token válido
        ```
        header = {
          ...
          "Authorization": "Bearer [el token de usuario cambia el password]}
        }
        ```
        : body json:
        ```
        body = {
          "new_password": password_for_the_user,
        }
        ```    
        :returns json message: 
        ```
        body = {
            "valid": [True o False],
            (solo si True) "role": rol}
        ```
        :returns status: HTTP_OK or HTTP_401(Unauthorized) or HTTP_500 (problems with DB)
        """
        token = request.headers.get('Authorization').split(' ')[1]
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = data['user_id'] or None
        if not user_id:
            return json_error(HTTPStatus.NOT_FOUND)
        
        user = db.session.execute(db.select(User).where(User.id == user_id)).scalars().first()
        if not user:
            return json_error(HTTPStatus.NOT_FOUND)
        
        new_password = request.get_json(silent=True).get('new_password', None)
        if not new_password:
            return json_error(HTTPStatus.BAD_REQUEST, JSON_ERROR)
        
        try:
            user.password = new_password
            db.session.commit()

        except:
            return json_error(HTTPStatus.INTERNAL_SERVER_ERROR,DB_ACCESS_ERROR)

        return json_message(HTTPStatus.OK, f'Password Usuari {user_id}:{user.username} ha canviat correctament')
    
                            
    @app.route('/users', methods = ['GET'])
    def get_users():
        user_list = db.session.execute(db.select(User)).scalars().all()
        return jsonify([u.to_dict() for u in user_list])
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("DATABASE:",app.config['SQLALCHEMY_DATABASE_URI'])
    app.run(host=app.config['AUTH_LISTEN_HOST'], port = app.config['AUTH_LISTEN_PORT'])