"""
Docstring for odontocare.auth-svc.server
"""
import os
import datetime as dt
from flask import Flask, request, jsonify
import jwt
from models import db, User
from tools import json_error,HTTPStatus


def create_app():
    app = Flask(__name__)
    # configuro les variables
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///users.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('OC_SECRET_KEY', 'development_secret')
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

    # POST: /login
    @app.route('/login', methods=['POST'])
    def login():
        response = request.get_json()
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
        return json_error(HTTPStatus.UNAUTHORIZED,'Wrong Credentials')
        

    @app.route('/validate/<int:user_id>', methods=['GET'])
    def validate(user_id):
        token = request.headers.get('Authorization')
        if not token:
            return json_error(HTTPStatus.UNAUTHORIZED,'Missing Token')
        
        try:
            # decodifico el token, si hi ha algun error no fa res i retorno un missatge false
            data = jwt.decode(token.split(" ")[1], app.config['SECRET_KEY'], algorithms=['HS256'])
            if data['user_id'] == user_id:
                return jsonify({'valid': True, 'role': data['role']}),200
        except Exception as e:
            pass
        return jsonify({'valid': False}), 403

    @app.route('/register', methods=['POST'])
    def register():
        data = request.get_json()
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

    @app.route('/users', methods = ['GET'])
    def get_users():
        user_list = db.session.execute(db.select(User)).scalars().all()
        return jsonify([u.to_dict() for u in user_list])
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host=app.config['AUTH_LISTEN_HOST'], port = app.config['AUTH_LISTEN_PORT'])