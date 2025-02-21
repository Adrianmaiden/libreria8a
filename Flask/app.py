from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
import os
import binascii
import bcrypt

app = Flask(__name__)

# Generar una clave secreta segura
app.secret_key = binascii.hexlify(os.urandom(24)).decode()

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
@app.route('/registrar', methods=['POST'])
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

# Ruta principal (Login)
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']

        try:
            conn = conectar_bd()
            cursor = conn.cursor(dictionary=True)

            # Buscar credenciales del usuario
            cursor.execute("""
                SELECT u.id_usuario, u.nombre_completo, u.rol, c.pass
                FROM Credenciales c
                JOIN Usuarios u ON c.id_usuario = u.id_usuario
                WHERE c.usuario = %s
            """, (usuario,))
            user_data = cursor.fetchone()

            if user_data and bcrypt.checkpw(contraseña.encode('utf-8'), user_data['pass'].encode('utf-8')):
                session['usuario'] = usuario
                session['id_usuario'] = user_data['id_usuario']
                session['rol'] = user_data['rol']

                if user_data['rol'] == 'Admin':
                    return redirect(url_for('admin'))
                else:
                    return redirect(url_for('cliente'))
            else:
                return "Credenciales incorrectas. <a href='/'>Intenta de nuevo</a>"

        except Exception as e:
            return f"Error: {e}"

        finally:
            cursor.close()
            conn.close()

    return render_template('index.html')

# Ruta para clientes
@app.route('/cliente')
def cliente():
    if 'usuario' in session and session['rol'] == 'Cliente':
        return render_template('cliente.html', usuario=session['usuario'])
    return redirect(url_for('login'))

# Ruta para administradores
@app.route('/admin')
def admin():
    if 'usuario' in session and session['rol'] == 'Admin':
        return render_template('admin.html', usuario=session['usuario'])
    return redirect(url_for('login'))

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Ruta para obtener libros en JSON
@app.route('/api/libros', methods=['GET'])
def obtener_libros():
    try:
        conn = conectar_bd()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Libros")
        libros = cursor.fetchall()
        return jsonify(libros)
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
