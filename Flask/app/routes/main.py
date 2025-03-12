from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Blueprint, flash
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
import os
import bcrypt
import re
import unicodedata

# Crear el Blueprint
main = Blueprint('main', __name__, static_folder='static', template_folder='templates')

# Función para convertir texto a slug
def slugify(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[-\s]+', '-', text)
    return text

# Registrar el filtro en el Blueprint
main.add_app_template_filter(slugify, name='slugify')

@main.route("/")
def index():
    usuario = session.get('usuario')
    return render_template("index.html", usuario=usuario)

@main.route("/about")
def about():
    return render_template("about.html")

@main.route("/glasses")
def glasses():
    return render_template("cliente.html")

# Configuración de las bases de datos
db_config_local = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'libreria'
}

db_config_rds = {
    'host': 'libreria-db.cztqrjvkhu8g.us-east-1.rds.amazonaws.com',
    'user': 'admin',
    'password': 'Str0ng3PassW0rD!',
    'database': 'libreria'
}

# Función para conectar a la base de datos con fallover
def conectar_bd():
    try:
        # Intentar conectar a la base de datos local
        connection = mysql.connector.connect(**db_config_local)
        if connection.is_connected():
            print("Conectado a la base de datos local.")
            return connection
    except Error as e:
        print(f"Error al conectar a la base de datos local: {e}")

    try:
        # Si falla, intentar conectar a la base de datos en RDS
        connection = mysql.connector.connect(**db_config_rds)
        if connection.is_connected():
            print("Conectado a la base de datos en RDS.")
            return connection
    except Error as e:
        print(f"Error al conectar a la base de datos en RDS: {e}")
        return None

def encriptar_contraseña(contraseña):
    # Genera un hash de la contraseña
    hash_bytes = bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt())
    # Convierte el hash a una cadena para almacenarlo en la base de datos
    return hash_bytes.decode('utf-8')

@main.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        correo = request.form.get('correo')
        telefono = request.form.get('telefono')
        direccion = request.form.get('direccion')
        usuario = request.form.get('usuario')
        contraseña = request.form.get('contraseña')

        if not nombre or not correo or not direccion or not usuario or not contraseña:
            flash("Todos los campos son obligatorios", "danger")
            return redirect(url_for('main.registrar'))

        # Encriptar la contraseña
        contraseña_encriptada = encriptar_contraseña(contraseña)

        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            # Insertar usuario en la tabla Usuarios
            cursor.execute("""
                INSERT INTO Usuarios (nombre_completo, correo, telefono, direccion, rol)
                VALUES (%s, %s, %s, %s, 'Cliente')
            """, (nombre, correo, telefono, direccion))

            id_usuario = cursor.lastrowid

            # Insertar credenciales en la tabla Credenciales
            cursor.execute("""
                INSERT INTO Credenciales (id_usuario, usuario, pass)
                VALUES (%s, %s, %s)
            """, (id_usuario, usuario, contraseña_encriptada))

            conn.commit()
            flash("Usuario registrado correctamente. <a href='/login'>Iniciar sesión</a>", "success")
            return redirect(url_for('main.login'))

        except mysql.connector.Error as e:
            flash(f"Error: {e}", "danger")
            return redirect(url_for('main.registrar'))

        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            if 'conn' in locals() and conn is not None:
                conn.close()

    return render_template('registrar.html')

@main.route('/registro_exitoso')
def registro_exitoso():
    return render_template('registro_exitoso.html')

@main.route('/cliente')
def cliente():
    if 'usuario' in session and session['rol'] == 'Cliente':
        try:
            conn = conectar_bd()
            cursor = conn.cursor(dictionary=True)

            # Obtener todos los libros
            cursor.execute("""
                SELECT l.*, c.nombre_categoria, TIMESTAMPDIFF(HOUR, l.fecha_creacion, NOW()) AS horas_desde_creacion
                FROM Libros l
                JOIN Categorias c ON l.id_categoria = c.id_categoria
            """)
            libros = cursor.fetchall()

            # Obtener calificaciones para cada libro
            for libro in libros:
                cursor.execute("""
                    SELECT AVG(valoracion) AS promedio, COUNT(*) AS total_calificaciones
                    FROM Calificaciones
                    WHERE id_libro = %s
                """, (libro['id_libro'],))
                calificacion = cursor.fetchone()
                libro['promedio_calificacion'] = calificacion['promedio'] if calificacion else 5.0
                libro['total_calificaciones'] = calificacion['total_calificaciones'] if calificacion else 0

                # Agregar lógica para el label "Nuevo"
                libro['es_nuevo'] = libro['horas_desde_creacion'] <= 2  # True si es nuevo, False si no

            return render_template('cliente.html', usuario=session['usuario'], libros=libros)

        except mysql.connector.Error as e:
            flash(f"Error: {e}", "danger")
            return redirect(url_for('main.cliente'))

        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            if 'conn' in locals() and conn is not None:
                conn.close()
    return redirect(url_for('main.login'))

@main.route('/calificar_libro/<int:id_libro>', methods=['POST'])
def calificar_libro(id_libro):
    if 'usuario' not in session:
        return redirect(url_for('main.login'))

    valoracion = request.form['valoracion']
    nombre_usuario = session['usuario']

    try:
        conn = conectar_bd()
        cursor = conn.cursor()

        # Insertar calificación en la tabla Calificaciones
        cursor.execute("""
            INSERT INTO Calificaciones (id_libro, id_usuario, valoracion, nombre_usuario)
            VALUES (%s, %s, %s, %s)
        """, (id_libro, session['id_usuario'], valoracion, nombre_usuario))

        conn.commit()
        flash("Calificación enviada correctamente", "success")
        return redirect(url_for('main.ver_libro', id_libro=id_libro))

    except mysql.connector.Error as e:
        flash(f"Error: {e}", "danger")
        return redirect(url_for('main.ver_libro', id_libro=id_libro))

    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn is not None:
            conn.close()

@main.route('/perfil')
def perfil():
    if 'usuario' not in session:
        return redirect(url_for('main.login'))

    try:
        conn = conectar_bd()
        cursor = conn.cursor(dictionary=True)

        # Obtener los datos del usuario
        cursor.execute("""
            SELECT u.nombre_completo, u.correo, u.telefono, u.direccion, c.usuario
            FROM Usuarios u
            JOIN Credenciales c ON u.id_usuario = c.id_usuario
            WHERE u.id_usuario = %s
        """, (session['id_usuario'],))
        usuario = cursor.fetchone()

        if usuario:
            return render_template('perfil.html', usuario=usuario)
        else:
            flash("Usuario no encontrado", "danger")
            return redirect(url_for('main.login'))

    except mysql.connector.Error as e:
        flash(f"Error: {e}", "danger")
        return redirect(url_for('main.perfil'))

    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn is not None:
            conn.close()

@main.route('/editar_perfil', methods=['GET', 'POST'])
def editar_perfil():
    if 'usuario' not in session:
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        nombre_completo = request.form['nombre_completo']
        correo = request.form['correo']
        telefono = request.form['telefono']
        direccion = request.form['direccion']

        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            # Actualizar los datos del usuario
            cursor.execute("""
                UPDATE Usuarios
                SET nombre_completo = %s, correo = %s, telefono = %s, direccion = %s
                WHERE id_usuario = %s
            """, (nombre_completo, correo, telefono, direccion, session['id_usuario']))

            conn.commit()
            flash("Perfil actualizado correctamente", "success")
            return redirect(url_for('main.perfil'))

        except mysql.connector.Error as e:
            flash(f"Error: {e}", "danger")
            return redirect(url_for('main.editar_perfil'))

        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            if 'conn' in locals() and conn is not None:
                conn.close()

    try:
        conn = conectar_bd()
        cursor = conn.cursor(dictionary=True)

        # Obtener los datos del usuario
        cursor.execute("""
            SELECT nombre_completo, correo, telefono, direccion
            FROM Usuarios
            WHERE id_usuario = %s
        """, (session['id_usuario'],))
        usuario = cursor.fetchone()

        if usuario:
            return render_template('editar_perfil.html', usuario=usuario)
        else:
            flash("Usuario no encontrado", "danger")
            return redirect(url_for('main.login'))

    except mysql.connector.Error as e:
        flash(f"Error: {e}", "danger")
        return redirect(url_for('main.editar_perfil'))

    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn is not None:
            conn.close()

@main.route('/libro/<int:id_libro>')
def ver_libro(id_libro):
    if 'usuario' not in session:
        return redirect(url_for('main.login'))

    try:
        conn = conectar_bd()
        cursor = conn.cursor(dictionary=True)

        # Obtener los detalles del libro
        cursor.execute("""
            SELECT l.*, c.nombre_categoria
            FROM Libros l
            JOIN Categorias c ON l.id_categoria = c.id_categoria
            WHERE l.id_libro = %s
        """, (id_libro,))
        libro = cursor.fetchone()

        if libro:
            # Obtener calificaciones para el libro
            cursor.execute("""
                SELECT AVG(valoracion) AS promedio, COUNT(*) AS total_calificaciones
                FROM Calificaciones
                WHERE id_libro = %s
            """, (id_libro,))
            calificacion = cursor.fetchone()
            libro['promedio_calificacion'] = calificacion['promedio'] if calificacion else 5.0
            libro['total_calificaciones'] = calificacion['total_calificaciones'] if calificacion else 0

            # Obtener el historial de calificaciones
            cursor.execute("""
                SELECT nombre_usuario, valoracion
                FROM Calificaciones
                WHERE id_libro = %s
            """, (id_libro,))
            historial_calificaciones = cursor.fetchall()

            # Obtener el conteo de calificaciones por nivel
            cursor.execute("""
                SELECT valoracion, COUNT(*) AS cantidad
                FROM Calificaciones
                WHERE id_libro = %s
                GROUP BY valoracion
            """, (id_libro,))
            conteo_calificaciones = cursor.fetchall()

            return render_template('detalles_libro.html', libro=libro, historial_calificaciones=historial_calificaciones, conteo_calificaciones=conteo_calificaciones)
        else:
            flash("Libro no encontrado", "danger")
            return redirect(url_for('main.cliente'))

    except mysql.connector.Error as e:
        flash(f"Error: {e}", "danger")
        return redirect(url_for('main.cliente'))

    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn is not None:
            conn.close()

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
                session['usuario'] = user_data['nombre_completo']
                session['id_usuario'] = user_data['id_usuario']
                session['rol'] = user_data['rol']

                if user_data['rol'] == 'Admin':
                    return redirect(url_for('admin.dashboard'))  # Redirigir al panel de administración
                else:
                    return redirect(url_for('main.cliente'))  # Redirigir al panel de cliente
            else:
                flash('Credenciales incorrectas. Intenta de nuevo.', 'danger')
                return render_template('login.html')

        except mysql.connector.Error as e:
            flash(f'Error: {e}', 'danger')
            return render_template('login.html')

        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            if 'conn' in locals() and conn is not None:
                conn.close()

    return render_template('login.html')

@main.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Aquí puedes manejar el envío del formulario de contacto
        name = request.form['Name']
        phone = request.form['Phone Number']
        email = request.form['Email']
        message = request.form['Message']

        # Aquí puedes agregar la lógica para enviar el correo o guardar la información en la base de datos
        flash("Mensaje enviado correctamente", "success")
        return redirect(url_for('main.contact'))

    return render_template('contact.html')

@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))

@main.route('/check-session')
def check_session():
    if 'usuario' in session:
        return jsonify(authenticated=True)
    else:
        return jsonify(authenticated=False)

@main.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response
