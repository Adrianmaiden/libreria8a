import mysql.connector
import bcrypt

# Configuración de conexión a MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'libreria'
}

# Conectar a la BD
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor(dictionary=True)

# Obtener todas las contraseñas no encriptadas
cursor.execute("SELECT id_login, pass FROM Credenciales")
usuarios = cursor.fetchall()

for usuario in usuarios:
    contraseña_plana = usuario['pass'].encode('utf-8')
    contraseña_encriptada = bcrypt.hashpw(contraseña_plana, bcrypt.gensalt()).decode('utf-8')

    # Actualizar contraseña en la base de datos
    cursor.execute("UPDATE Credenciales SET pass = %s WHERE id_login = %s", (contraseña_encriptada, usuario['id_login']))
    print(f"Contraseña de usuario {usuario['id_login']} encriptada.")

conn.commit()
cursor.close()
conn.close()
print("✅ Todas las contraseñas han sido encriptadas correctamente.")
