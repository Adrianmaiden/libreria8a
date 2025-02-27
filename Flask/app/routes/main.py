from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Blueprint
import mysql.connector
import os
import binascii
import bcrypt

main = Blueprint('main', __name__, static_folder='static', template_folder='templates')

@main.route("/")
def index():
    return render_template("index.html")

@main.route("/about")
def about():
    return render_template("about.html")

@main.route("/glasses")
def glasses():
    return render_template("cliente.html")

# Configuración de la conexión a MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'libreria'
}

# Función para conectar a la base de datos
def conectar_bd():
    return mysql.connector.connect(**db_config)

# Función para encriptar la contraseña antes de guardarla en la BD
def encriptar_contraseña(contraseña):
    return bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Ruta para registrar un usuario (Cliente o Admin)
@main.route('/registrar', methods=['POST'])
def registrar():
    nombre = request.form['nombre']
    correo = request.form['correo']
    telefono = request.form['telefono']
    direccion = request.form['direccion']
    rol = request.form['rol']  # Cliente o Admin
    usuario = request.form['usuario']
    contraseña = request.form['contraseña']

    contraseña_encriptada = encriptar_contraseña(contraseña)

    try:
        conn = conectar_bd()
        cursor = conn.cursor()

        # Insertar usuario en la tabla Usuarios
        cursor.execute("""
            INSERT INTO Usuarios (nombre_completo, correo, telefono, direccion, rol)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, correo, telefono, direccion, rol))
        
        id_usuario = cursor.lastrowid

        # Insertar credenciales en la tabla Credenciales
        cursor.execute("""
            INSERT INTO Credenciales (id_usuario, usuario, pass)
            VALUES (%s, %s, %s)
        """, (id_usuario, usuario, contraseña_encriptada))

        conn.commit()
        return "Usuario registrado correctamente. <a href='/'>Iniciar sesión</a>"

    except Exception as e:
        return f"Error: {e}"

    finally:
        cursor.close()
        conn.close()

@main.route('/cliente')
def cliente():
    if 'usuario' in session and session['rol'] == 'Cliente':
        return render_template('cliente.html', usuario=session['usuario'])
    return redirect(url_for('main.login'))

@main.route('/admin')
def admin_panel():
    if 'usuario' in session and session['rol'] == 'Admin':  # Corregido
        return render_template('admin_panel.html')
    return redirect(url_for('main.login'))  # Corregido
    
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']

        try:
            conn = conectar_bd()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT u.id_usuario, u.nombre_completo, u.rol, c.pass
                FROM Credenciales c
                JOIN Usuarios u ON c.id_usuario = u.id_usuario
                WHERE c.usuario = %s
            """, (usuario,))
            user_data = cursor.fetchone()

            if user_data and bcrypt.checkpw(contraseña.encode('utf-8'), user_data['pass'].encode('utf-8')):
                session['usuario'] = user_data['nombre_completo']  # Nombre completo
                session['id_usuario'] = user_data['id_usuario']
                session['rol'] = user_data['rol']

                if user_data['rol'] == 'Admin':
                    return redirect(url_for('main.admin_panel'))  # Corregido
                else:
                    return redirect(url_for('main.cliente'))  # Corregido
            else:
                mensaje = {'texto': 'Credenciales incorrectas. Intenta de nuevo.', 'tipo': 'danger'}
                return render_template('login.html', mensaje=mensaje)

        except Exception as e:
            mensaje = {'texto': f'Error: {e}', 'tipo': 'danger'}
            return render_template('login.html', mensaje=mensaje)

        finally:
            cursor.close()
            conn.close()

    return render_template('login.html')
    
# Ruta para cerrar sesión
@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))