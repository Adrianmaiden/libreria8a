from flask import Flask
import os
import binascii
from .routes.main import main
from .routes.admin import admin
from flask_uploads import UploadSet, configure_uploads, IMAGES


def create_app():
    app = Flask(__name__, static_folder='static')
    app.secret_key = binascii.hexlify(os.urandom(24)).decode()

    # Configuración (importa desde config.py si es necesario)
    app.config.from_object("config")
    app.config['UPLOADED_PHOTOS_DEST'] = 'static/images/Libros'  # Carpeta donde se guardarán las imágenes
    app.config['UPLOADED_PHOTOS_ALLOW'] = IMAGES  # Permitir solo imágenes
    photos = UploadSet('photos', IMAGES)
    configure_uploads(app, photos)

    # Importar Blueprints
    app.register_blueprint(main)
    app.register_blueprint(admin, url_prefix='/admin')

    return app
