# app/db.py
import mysql.connector

def conectar_bd():
    conn = mysql.connector.connect(
        'host': 'libreria-db.cztqrjvkhu8g.us-east-1.rds.amazonaws.com',
        'user': 'admin',
        'password': 'Str0ng3PassW0rD!',
        'database': 'libreria'
    )
    return conn