import os
from flask import Flask

from bp import admin_bp , auth_bp, agenda_bp
from octools import json_error, HTTPStatus, OCERR


def create_app():
    app=Flask(__name__)

    app.config['OC_API_LISTEN_HOST'] = os.environ.get('OC_API_LISTEN_HOST','0.0.0.0')
    app.config['OC_API_LISTEN_PORT'] = os.environ.get('OC_API_LISTEN_PORT', 4000)

    app.config['SECRET_KEY'] = os.environ.get('OC_SECRET_KEY', '1234')

    app.config['OC_AUTH_SVC'] = os.environ.get('OC_AUTH_SVC','http://localhost:4001')
    app.config['OC_ADMIN_SVC'] = os.environ.get('OC_ADMIN_SVC','http://localhost:4002')
    app.config['OC_AGENDA_SVC'] = os.environ.get('OC_AGENDA_SVC','http://localhost:4003')


    # defineixo error per metode o endpoint inexistent
    @app.errorhandler(404)
    def non_existant_route(error):
        return json_error(HTTPStatus.NOT_FOUND, OCERR.NOT_FOUND)
    
    @app.errorhandler(405)
    def non_allowed_method(error):
        return json_error(HTTPStatus.METHOD_NOT_ALLOWED, OCERR.METHOD_NOT_ALLOWED)
    

    # registro els blueprints
    try:
        app.register_blueprint(auth_bp, url_prefix="/api/v1/users")
        app.register_blueprint(admin_bp, url_prefix="/api/v1/admin")
        app.register_blueprint(agenda_bp, url_prefix="/api/v1/agenda")
    except Exception as e:
        # si no puc resitrar blueprints, surto applicació
        print(f'Error Registering Blueprints:\n{e}')
        exit() 
        

    return app
 
# blucle principal
if __name__ == "__main__":
    app= create_app()
    print(app.config['OC_AUTH_SVC'] )
    print(app.config['OC_ADMIN_SVC'] )
    print(app.config['OC_AGENDA_SVC'])

    app.run(
        host=app.config["OC_API_LISTEN_HOST"],
        port=app.config["OC_API_LISTEN_PORT"]
    )

