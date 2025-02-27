from flask import Flask
import os
import binascii
from .routes.main import main

def create_app():
    app = Flask(__name__, static_folder='static')
    app.secret_key = binascii.hexlify(os.urandom(24)).decode()

    # Configuración (importa desde config.py si es necesario)
    app.config.from_object("config")

    # Importar Blueprints
    app.register_blueprint(main)

    return app
