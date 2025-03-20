from flask import Flask
import os
import binascii
from flask_uploads import UploadSet, configure_uploads, IMAGES
from .extensions import mail  # Importar mail desde extensions.py

def create_app():
    app = Flask(__name__, static_folder='static')
    app.secret_key = binascii.hexlify(os.urandom(24)).decode()

    # Configuración (importa desde config.py si es necesario)
    app.config.from_object("config")
    app.config['UPLOADED_PHOTOS_DEST'] = 'static/images/Libros'  # Carpeta donde se guardarán las imágenes
    app.config['UPLOADED_PHOTOS_ALLOW'] = IMAGES  # Permitir solo imágenes
    photos = UploadSet('photos', IMAGES)
    configure_uploads(app, photos)

    # Configuración de Flask-Mail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Servidor SMTP de Gmail
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = '20223tn150@utez.edu.mx'  # Tu correo
    app.config['MAIL_PASSWORD'] = 'roxd ctzi flgg ubij'  # Tu contraseña de aplicación (no la de tu correo)
    app.config['MAIL_DEFAULT_SENDER'] = 'cyphersecu@gmail.com'

    # Inicializar Flask-Mail
    mail.init_app(app)

    # Importar Blueprints
    from .routes.main import main
    from .routes.admin import admin

    app.register_blueprint(main)
    app.register_blueprint(admin, url_prefix='/admin')

    return app