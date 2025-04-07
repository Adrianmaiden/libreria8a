from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
import mysql.connector
from mysql.connector import Error
import bcrypt  # Importar bcrypt directamente
from ..extensions import mail  # Importar mail desde extensions.py
import yaml
import os

# Crear un Blueprint para las rutas de administración
admin = Blueprint('admin', __name__, static_folder='static', template_folder='templates/admin')

# 1. Primero define la función de carga
def load_admin_config():
    """Carga la configuración desde admin_config.yaml"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'admin_config.yaml')
        
        if not os.path.exists(config_path):
            current_app.logger.error(f"Archivo de configuración no encontrado: {config_path}")
            return {}

        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config if isinstance(config, dict) else {}

    except Exception as e:
        current_app.logger.error(f"Error cargando configuración: {str(e)}")
        return {}

# 2. Luego carga la configuración
admin_config = load_admin_config()

# 3. Context processor para hacer admin_config disponible en templates
@admin.context_processor
def inject_admin_config():
    return {'admin_config': admin_config}

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
    connection = None
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
    
from flask import request, flash, redirect, url_for
import yaml
from pathlib import Path

@admin.route('/config-editor', methods=['GET', 'POST'])
def config_editor():
    if 'usuario' not in session or session.get('rol') != 'Admin':
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('main.login'))
    
    config_path = Path(__file__).parent.parent / 'admin_config.yaml'
    
    if request.method == 'POST':
        try:
            # Obtener los datos del formulario
            new_config = {
                'dashboard': {
                    'title': request.form.get('dashboard_title'),
                    'welcome_message': request.form.get('welcome_message'),
                    'menu': [],
                    'logout': {
                        'visible': request.form.get('logout_visible') == 'on',
                        'icon': request.form.get('logout_icon'),
                        'text': request.form.get('logout_text'),
                        'class': request.form.get('logout_class'),
                        'position': request.form.get('logout_position')
                    }
                }
            }
            
            # Procesar los ítems del menú
            menu_items = request.form.getlist('menu_name[]')
            for i, name in enumerate(menu_items):
                new_config['dashboard']['menu'].append({
                    'name': name,
                    'icon': request.form.getlist('menu_icon[]')[i],
                    'url': request.form.getlist('menu_url[]')[i],
                    'order': int(request.form.getlist('menu_order[]')[i])
                })
            
            # Escribir el archivo YAML
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(new_config, f, allow_unicode=True)
            
            flash('Configuración actualizada correctamente', 'success')
            return redirect(url_for('admin.config_editor'))
        
        except Exception as e:
            flash(f'Error al guardar la configuración: {str(e)}', 'danger')
    
    # Cargar la configuración actual para mostrar en el formulario
    with open(config_path, 'r', encoding='utf-8') as f:
        current_config = yaml.safe_load(f) or {}
    
    return render_template('admin/config_editor.html', 
                         config=current_config.get('dashboard', {}))

@admin.route('/dashboard')
def dashboard():
    if 'usuario' not in session or session.get('rol') != 'Admin':
        flash('Debes iniciar sesión como administrador', 'danger')
        return redirect(url_for('main.login'))

    try:
        conn = conectar_bd()
        if not conn:
            raise Exception("Error de conexión a la base de datos")
            
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT COUNT(*) AS total_usuarios FROM Usuarios WHERE rol = 'Cliente'")
            total_usuarios = cursor.fetchone()['total_usuarios']

            cursor.execute("SELECT COUNT(*) AS total_libros FROM Libros")
            total_libros = cursor.fetchone()['total_libros']

            ventas_hoy = 0

        # Cargar la configuración YAML
        config_path = Path(__file__).parent.parent / 'admin_config.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            admin_config = yaml.safe_load(f) or {}

        return render_template('admin/dashboard.html',
                            usuario=session['usuario'],
                            total_usuarios=total_usuarios,
                            total_libros=total_libros,
                            ventas_hoy=ventas_hoy,
                            admin_config=admin_config)  # ¡Asegúrate de pasar esto!

    except Exception as e:
        current_app.logger.error(f"Error en dashboard: {str(e)}")
        return render_template('admin/error.html',
                            error_message="Error al cargar los datos del dashboard")

# Ruta para la gestión de libros
@admin.route('/libros')
def libros():
    if 'usuario' in session and session['rol'] == 'Admin':
        try:
            conn = conectar_bd()
            cursor = conn.cursor(dictionary=True)

            # Obtener todos los libros con la categoría
            cursor.execute("""
                SELECT l.*, c.nombre_categoria
                FROM Libros l
                JOIN Categorias c ON l.id_categoria = c.id_categoria
            """)
            libros = cursor.fetchall()

            return render_template('admin/libros.html', libros=libros)

        except mysql.connector.Error as e:
            flash(f"Error: {e}", "danger")
            return redirect(url_for('admin.libros'))

        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    return redirect(url_for('main.login'))


# Ruta para agregar un libro
from flask import request, redirect, url_for, flash

from flask import request, redirect, url_for, flash

from flask import request, redirect, url_for, flash

@admin.route('/libros/agregar', methods=['GET', 'POST'])
def agregar_libro():
    if 'usuario' in session and session['rol'] == 'Admin':
        if request.method == 'POST':
            titulo = request.form.get('titulo')
            autor = request.form.get('autor')
            editorial = request.form.get('editorial')
            anio_publicacion = request.form.get('anio_publicacion')
            precio = request.form.get('precio')
            stock = request.form.get('stock')
            id_categoria = request.form.get('id_categoria')
            nueva_categoria = request.form.get('nueva_categoria')
            portada = request.files.get('portada')

            if not titulo or not autor or not editorial or not anio_publicacion or not precio or not stock:
                flash("Todos los campos son obligatorios", "danger")
                return redirect(url_for('admin.agregar_libro'))

            if nueva_categoria:
                try:
                    conn = conectar_bd()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO Categorias (nombre_categoria) VALUES (%s)", (nueva_categoria,))
                    conn.commit()
                    id_categoria = cursor.lastrowid  # Obtener el ID de la nueva categoría
                except mysql.connector.Error as e:
                    flash(f"Error al agregar nueva categoría: {e}", "danger")
                    return redirect(url_for('admin.agregar_libro'))
                finally:
                    if 'cursor' in locals():
                        cursor.close()
                    if 'conn' in locals():
                        conn.close()

            if portada:
                try:
                    filename = photos.save(portada)
                except UploadNotAllowed:
                    flash("Tipo de archivo no permitido", "danger")
                    return redirect(url_for('admin.agregar_libro'))

            try:
                conn = conectar_bd()
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO Libros (titulo, autor, editorial, anio_publicacion, precio, stock_disponible, id_categoria)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (titulo, autor, editorial, anio_publicacion, precio, stock, id_categoria))

                conn.commit()
                flash("Libro agregado correctamente", "success")
                return redirect(url_for('admin.libros'))

            except mysql.connector.Error as e:
                flash(f"Error: {e}", "danger")
                return redirect(url_for('admin.agregar_libro'))

            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()

        else:
            # Cargar las categorías para el formulario
            try:
                conn = conectar_bd()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT id_categoria, nombre_categoria FROM Categorias")
                categorias = cursor.fetchall()
            except mysql.connector.Error as e:
                flash(f"Error al cargar las categorías: {e}", "danger")
                categorias = []
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()

            return render_template('admin/agregar_libro.html', categorias=categorias)
    return redirect(url_for('main.login'))

from flask import request, redirect, url_for, flash

@admin.route('/libros/editar/<int:id>', methods=['GET', 'POST'])
def editar_libro(id):
    if 'usuario' in session and session['rol'] == 'Admin':
        if request.method == 'POST':
            titulo = request.form.get('titulo')
            autor = request.form.get('autor')
            editorial = request.form.get('editorial')
            anio_publicacion = request.form.get('anio_publicacion')
            precio = request.form.get('precio')
            stock = request.form.get('stock')
            id_categoria = request.form.get('id_categoria')
            nueva_categoria = request.form.get('nueva_categoria')
            nueva_portada = request.files.get('portada')

            if nueva_categoria:
                try:
                    conn = conectar_bd()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO Categorias (nombre_categoria) VALUES (%s)", (nueva_categoria,))
                    conn.commit()
                    id_categoria = cursor.lastrowid  # Obtener el ID de la nueva categoría
                except mysql.connector.Error as e:
                    flash(f"Error al agregar nueva categoría: {e}", "danger")
                    return redirect(url_for('admin.editar_libro', id=id))
                finally:
                    if 'cursor' in locals():
                        cursor.close()
                    if 'conn' in locals():
                        conn.close()

            if nueva_portada:
                try:
                    filename = photos.save(nueva_portada)
                    # Aquí puedes hacer algo con 'filename' si es necesario
                except UploadNotAllowed:
                    flash("Tipo de archivo no permitido", "danger")
                    return redirect(url_for('admin.editar_libro', id=id))

            try:
                conn = conectar_bd()
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE Libros
                    SET titulo = %s, autor = %s, editorial = %s, anio_publicacion = %s, precio = %s, stock_disponible = %s, id_categoria = %s
                    WHERE id_libro = %s
                """, (titulo, autor, editorial, anio_publicacion, precio, stock, id_categoria, id))

                conn.commit()
                flash("Libro editado correctamente", "success")
                return redirect(url_for('admin.libros'))

            except mysql.connector.Error as e:
                flash(f"Error: {e}", "danger")
                return redirect(url_for('admin.editar_libro', id=id))

            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()

        else:
            try:
                conn = conectar_bd()
                cursor = conn.cursor(dictionary=True)

                # Obtener el libro
                cursor.execute("SELECT * FROM Libros WHERE id_libro = %s", (id,))
                libro = cursor.fetchone()

                # Obtener las categorías
                cursor.execute("SELECT id_categoria, nombre_categoria FROM Categorias")
                categorias = cursor.fetchall()

            except mysql.connector.Error as e:
                flash(f"Error: {e}", "danger")
                return redirect(url_for('admin.libros'))
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()

            return render_template('admin/editar_libro.html', libro=libro, categorias=categorias)
    else:
        flash('Acceso no autorizado. Debes iniciar sesión como administrador.', 'danger')
        return redirect(url_for('main.login'))

    
@admin.route('/libros/eliminar/<int:id>', methods=['POST'])
def eliminar_libro(id):
    if 'usuario' in session and session['rol'] == 'Admin':
        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            # Eliminar el libro de la tabla Libros
            cursor.execute("DELETE FROM Libros WHERE id_libro = %s", (id,))

            conn.commit()
            flash("Libro eliminado correctamente", "success")

        except mysql.connector.Error as e:
            flash(f"Error: {e}", "danger")

        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

        return redirect(url_for('admin.libros'))
    return redirect(url_for('main.login'))


@admin.route('/usuarios')
def usuarios():
    if 'usuario' in session and session['rol'] == 'Admin':
        try:
            conn = conectar_bd()
            cursor = conn.cursor(dictionary=True)

            # Obtener todos los usuarios (solo clientes) incluyendo la dirección y el teléfono
            cursor.execute("""
                SELECT u.id_usuario, u.nombre_completo, u.correo, u.direccion, u.telefono, c.usuario
                FROM Usuarios u
                JOIN Credenciales c ON u.id_usuario = c.id_usuario
                WHERE u.rol = 'Cliente'
            """)
            usuarios = cursor.fetchall()

            return render_template('admin/usuarios.html', usuarios=usuarios)

        except mysql.connector.Error as e:
            flash(f"Error al obtener la lista de usuarios: {e}", "danger")
            return redirect(url_for('admin.usuarios'))

        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    else:
        flash('Acceso no autorizado. Debes iniciar sesión como administrador.', 'danger')
        return redirect(url_for('main.login'))


# Ruta para agregar un usuario
@admin.route('/usuarios/agregar', methods=['GET', 'POST'])
def agregar_usuario():
    if 'usuario' in session and session['rol'] == 'Admin':
        if request.method == 'POST':
            nombre = request.form.get('nombre')
            correo = request.form.get('correo')
            usuario = request.form.get('usuario')
            contraseña = request.form.get('contraseña')
            direccion = request.form.get('direccion')
            telefono = request.form.get('telefono')  # Captura el campo teléfono

            if not nombre or not correo or not usuario or not contraseña or not direccion or not telefono:
                flash("Todos los campos son obligatorios", "danger")
                return redirect(url_for('admin.agregar_usuario'))

            try:
                conn = conectar_bd()
                cursor = conn.cursor()

                # Hashear la contraseña con bcrypt
                hashed_password = bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt())

                # Insertar en la tabla Usuarios
                cursor.execute("""
                    INSERT INTO Usuarios (nombre_completo, correo, direccion, telefono, rol)
                    VALUES (%s, %s, %s, %s, 'Cliente')
                """, (nombre, correo, direccion, telefono))

                id_usuario = cursor.lastrowid

                # Insertar en la tabla Credenciales
                cursor.execute("""
                    INSERT INTO Credenciales (id_usuario, usuario, pass)
                    VALUES (%s, %s, %s)
                """, (id_usuario, usuario, hashed_password))

                conn.commit()
                flash("Usuario agregado correctamente", "success")
                return redirect(url_for('admin.usuarios'))

            except mysql.connector.Error as e:
                flash(f"Error al agregar usuario: {e}", "danger")
                return redirect(url_for('admin.agregar_usuario'))

            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()

        return render_template('admin/agregar_usuario.html')
    return redirect(url_for('main.login'))


@admin.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    if 'usuario' in session and session['rol'] == 'Admin':
        if request.method == 'POST':
            nombre = request.form.get('nombre')
            correo = request.form.get('correo')
            usuario = request.form.get('usuario')
            contraseña = request.form.get('contraseña')
            direccion = request.form.get('direccion')
            telefono = request.form.get('telefono')  # Captura el campo teléfono

            try:
                conn = conectar_bd()
                cursor = conn.cursor()

                if contraseña:
                    hashed_password = bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt())
                    cursor.execute("""
                        UPDATE Credenciales
                        SET usuario = %s, pass = %s
                        WHERE id_usuario = %s
                    """, (usuario, hashed_password, id))
                else:
                    cursor.execute("""
                        UPDATE Credenciales
                        SET usuario = %s
                        WHERE id_usuario = %s
                    """, (usuario, id))

                cursor.execute("""
                    UPDATE Usuarios
                    SET nombre_completo = %s, correo = %s, direccion = %s, telefono = %s
                    WHERE id_usuario = %s
                """, (nombre, correo, direccion, telefono, id))

                conn.commit()
                flash("Usuario editado correctamente", "success")
                return redirect(url_for('admin.usuarios'))

            except mysql.connector.Error as e:
                flash(f"Error al editar usuario: {e}", "danger")
                return redirect(url_for('admin.editar_usuario', id=id))

            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()

        else:
            try:
                conn = conectar_bd()
                cursor = conn.cursor(dictionary=True)

                cursor.execute("""
                    SELECT u.id_usuario, u.nombre_completo, u.correo, u.direccion, u.telefono, c.usuario
                    FROM Usuarios u
                    JOIN Credenciales c ON u.id_usuario = c.id_usuario
                    WHERE u.id_usuario = %s
                """, (id,))
                usuario = cursor.fetchone()

                return render_template('admin/editar_usuario.html', usuario=usuario)

            except mysql.connector.Error as e:
                flash(f"Error al obtener datos del usuario: {e}", "danger")
                return redirect(url_for('admin.usuarios'))

            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()
    else:
        flash('Acceso no autorizado. Debes iniciar sesión como administrador.', 'danger')
        return redirect(url_for('main.login'))



# Ruta para eliminar un usuario
@admin.route('/usuarios/eliminar/<int:id>', methods=['POST'])
def eliminar_usuario(id):
    if 'usuario' in session and session['rol'] == 'Admin':
        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            # Eliminar de la tabla Credenciales
            cursor.execute("DELETE FROM Credenciales WHERE id_usuario = %s", (id,))

            # Eliminar de la tabla Usuarios
            cursor.execute("DELETE FROM Usuarios WHERE id_usuario = %s", (id,))

            conn.commit()
            flash("Usuario eliminado correctamente", "success")

        except mysql.connector.Error as e:
            flash(f"Error: {e}", "danger")

        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

        return redirect(url_for('admin.usuarios'))
    return redirect(url_for('main.login'))

@admin.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))

# Ruta para verificar sesión
@admin.route('/check-session')
def check_session():
    if 'usuario' in session:
        return jsonify(authenticated=True)
    else:
        return jsonify(authenticated=False)

# Función para controlar el almacenamiento en caché
@admin.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response