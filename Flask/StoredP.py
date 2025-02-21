from flask import Flask, jsonify, render_template_string
import mysql.connector

app = Flask(__name__)

# Configuración de la conexión a MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'libreria'
}

@app.route('/')
def inicio():
    # Página de bienvenida con un enlace a /libros
    return render_template_string("""
        <html>
            <head><title>API de Libros</title></head>
            <body>
                <h1>Bienvenido a la API de Libros</h1>
                <p>Haz clic en el siguiente enlace para ver los libros:</p>
                <a href="{{ url_for('obtener_libros') }}">Ver Libros</a>
            </body>
        </html>
    """)

@app.route('/libros', methods=['GET'])
def obtener_libros():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Llamar al procedimiento almacenado
        cursor.callproc('mostrar_libros')

        # Verificar si el procedimiento devuelve resultados
        libros = []
        for result in cursor.stored_results():
            libros = result.fetchall()

        # Si no hay resultados, muestra el error
        if not libros:
            return jsonify({"error": "No se encontraron libros."})

        return jsonify(libros)  # Devuelve los datos en formato JSON

    except Exception as e:
        # Imprimir el error para depuración
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)})

    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)

