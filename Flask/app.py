from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
import os
import binascii

app = Flask(__name__)

# Generar una clave secreta segura
app.secret_key = binascii.hexlify(os.urandom(24)).decode()

# Configuración de la conexión a MySQL
db_config = {
    'host': 'localhost',  # Cambia si es un servidor remoto
    'user': 'root',
    'password': 'root',
    'database': 'libreria'
}


# Función para conectar a la base de datos
def conectar_bd():
    return mysql.connector.connect(**db_config)


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

            if user_data and contraseña == user_data['pass']:  # ⚠️ Mejor encriptar contraseñas en producción
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

