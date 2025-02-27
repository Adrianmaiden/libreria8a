import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "mi_clave_secreta")
    DEBUG = True
