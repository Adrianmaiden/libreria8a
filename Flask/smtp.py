import smtplib
from email.mime.text import MIMEText

# Configuración del correo
smtp_server = 'smtp.gmail.com'
smtp_port = 587
username = '20223tn150@utez.edu.mx'
password = 'roxd ctzi flgg ubij'

# Crear el mensaje
msg = MIMEText('Este es un mensaje de prueba.')
msg['Subject'] = 'Prueba de Correo'
msg['From'] = username
msg['To'] = 'adbarrosobarrios@gmail.com'

# Enviar el correo
try:
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(username, password)
        server.sendmail(username, [msg['To']], msg.as_string())
    print("Correo enviado exitosamente.")
except Exception as e:
    print(f"Error al enviar el correo: {e}")
