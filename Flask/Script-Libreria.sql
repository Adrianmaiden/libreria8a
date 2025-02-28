CREATE DATABASE IF NOT EXISTS libreria;
USE libreria;

-- Tabla de Usuarios
CREATE TABLE Usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre_completo VARCHAR(255) NOT NULL,
    correo VARCHAR(255) NOT NULL UNIQUE,
    telefono VARCHAR(20),
    direccion TEXT NOT NULL,
    rol ENUM('Cliente', 'Admin') NOT NULL DEFAULT 'Cliente'
);

-- Tabla de Credenciales
CREATE TABLE Credenciales (
    id_login INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    usuario VARCHAR(255) NOT NULL UNIQUE,
    pass VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario)
);

-- Tabla de Categorías de Libros
CREATE TABLE Categorias (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre_categoria VARCHAR(100) NOT NULL UNIQUE
);

-- Tabla de Libros
CREATE TABLE Libros (
    id_libro INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    autor VARCHAR(255) NOT NULL,
    editorial VARCHAR(255),
    anio_publicacion YEAR,
    precio DECIMAL(10, 2) NOT NULL,
    stock_disponible INT NOT NULL DEFAULT 0,
    id_categoria INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_categoria) REFERENCES Categorias(id_categoria)
);

-- Tabla de Órdenes de Compra
CREATE TABLE Ordenes (
    id_orden INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    fecha_orden TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('pendiente', 'pagado', 'enviado', 'entregado') NOT NULL DEFAULT 'pendiente',
    monto_total DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario)
);

-- Tabla de Detalle de la Orden
CREATE TABLE DetalleOrden (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_orden INT NOT NULL,
    id_libro INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (id_orden) REFERENCES Ordenes(id_orden),
    FOREIGN KEY (id_libro) REFERENCES Libros(id_libro)
);

-- Tabla de Pagos
CREATE TABLE Pagos (
    id_pago INT AUTO_INCREMENT PRIMARY KEY,
    id_orden INT NOT NULL,
    metodo_pago ENUM('tarjeta', 'OXXO', 'PayPal') NOT NULL,
    estado_pago ENUM('pendiente', 'confirmado', 'fallido') NOT NULL DEFAULT 'pendiente',
    fecha_pago TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_orden) REFERENCES Ordenes(id_orden)
);

-- Tabla de Envíos
CREATE TABLE Envios (
    id_envio INT AUTO_INCREMENT PRIMARY KEY,
    id_orden INT NOT NULL,
    id_usuario INT NOT NULL,
    direccion_envio TEXT NOT NULL,
    empresa_envio VARCHAR(50),
    estado_envio ENUM('pendiente', 'en camino', 'entregado') NOT NULL DEFAULT 'pendiente',
    fecha_envio TIMESTAMP NULL DEFAULT NULL,
    FOREIGN KEY (id_orden) REFERENCES Ordenes(id_orden),
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario)
);

CREATE TABLE Calificaciones (
    id_calificacion INT AUTO_INCREMENT PRIMARY KEY,
    id_libro INT NOT NULL,
    id_usuario INT NOT NULL,
    nombre_usuario VARCHAR(255) NOT NULL,
    valoracion INT NOT NULL CHECK (valoracion BETWEEN 1 AND 5),
    fecha_calificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_libro) REFERENCES Libros(id_libro),
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario)
);
