import os
from flask import Flask

from bp import admin_bp , auth_bp, agenda_bp

def create_app():
    app=Flask(__name__)

    app.config['OC_API_LISTEN_HOST'] = os.environ.get('OC_API_LISTEN_HOST','0.0.0.0')
    app.config['OC_API_LISTEN_PORT'] = os.environ.get('OC_API_LISTEN_PORT', 4000)

    app.config['OC_AUTH_SVC'] = os.environ.get('OC_AUTH_SVC','http://localhost:4001')
    app.config['OC_ADMIN_SVC'] = os.environ.get('OC_ADMIN','http://localhost:4002')
    app.config['OC_AGEBDA_SVC'] = os.environ.get('OC_AGENDA_SVC','http://localhost:4003')
    #TODO: Algo configure the possibility to configure the ports (or use default port)

    # registro els blueprints
    try:
        app.register_blueprint(auth_bp, url_prefix="/api/v1")
        app.register_blueprint(admin_bp, url_prefix="/api/v1")
        app.register_blueprint(agenda_bp, url_prefix="/api/v1")
    except Exception as e:
        # si no puc resitrar blueprints, surto applicació
        print(f'Error Registering Blueprints:\n{e}')
        exit() 
        

    return app
 
# blucle principal
if __name__ == "__main__":
    app= create_app()
    app.run(
        host=app.config["OC_API_LISTEN_HOST"],
        port=app.config["OC_API_LISTEN_PORT"]
    )

