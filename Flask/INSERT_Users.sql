INSERT INTO Usuarios (nombre_completo, correo, telefono, direccion, rol)
VALUES ('Admin Principal', 'admin@email.com', '1234567890', 'Calle 123', 'Admin');

INSERT INTO Usuarios (nombre_completo, correo, telefono, direccion, rol)
VALUES ('Cliente Ejemplo', 'cliente@email.com', '0987654321', 'Avenida 456', 'Cliente');

INSERT INTO Credenciales (id_usuario, usuario, pass)
VALUES (1, 'admin', 'admin123'), (2, 'cliente', 'cliente123');