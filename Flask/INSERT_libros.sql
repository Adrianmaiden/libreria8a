INSERT INTO Categorias (nombre_categoria) VALUES ('Fantasía') ON DUPLICATE KEY UPDATE id_categoria=id_categoria;
INSERT INTO Libros (titulo, autor, editorial, anio_publicacion, precio, stock_disponible, id_categoria) 
VALUES ('Harry Potter y la Piedra Filosofal', 'J.K. Rowling', 'Salamandra', 1997, 299.99, 50, 
    (SELECT id_categoria FROM Categorias WHERE nombre_categoria='Fantasía' LIMIT 1));

INSERT INTO Categorias (nombre_categoria) VALUES ('Drama') ON DUPLICATE KEY UPDATE id_categoria=id_categoria;
INSERT INTO Libros (titulo, autor, editorial, anio_publicacion, precio, stock_disponible, id_categoria) 
VALUES ('El Jardín de las Mariposas', 'Dot Hutchison', 'Urano', 2016, 350.00, 30, 
    (SELECT id_categoria FROM Categorias WHERE nombre_categoria='Drama' LIMIT 1));

INSERT INTO Categorias (nombre_categoria) VALUES ('Romance') ON DUPLICATE KEY UPDATE id_categoria=id_categoria;
INSERT INTO Libros (titulo, autor, editorial, anio_publicacion, precio, stock_disponible, id_categoria) 
VALUES ('En Agosto Nos Vemos', 'Gabriel García Márquez', 'Penguin Random House', 2023, 420.00, 40, 
    (SELECT id_categoria FROM Categorias WHERE nombre_categoria='Romance' LIMIT 1));

INSERT INTO Categorias (nombre_categoria) VALUES ('Misterio') ON DUPLICATE KEY UPDATE id_categoria=id_categoria;
INSERT INTO Libros (titulo, autor, editorial, anio_publicacion, precio, stock_disponible, id_categoria) 
VALUES ('La Ciudad y Sus Muros Secretos', 'Haruki Murakami', 'Tusquets', 2023, 380.00, 25, 
    (SELECT id_categoria FROM Categorias WHERE nombre_categoria='Misterio' LIMIT 1));

INSERT INTO Categorias (nombre_categoria) VALUES ('Tecnología') ON DUPLICATE KEY UPDATE id_categoria=id_categoria;
INSERT INTO Libros (titulo, autor, editorial, anio_publicacion, precio, stock_disponible, id_categoria) 
VALUES ('Libro Cypher', 'Autor Desconocido', 'Cypher Publishing', 2023, 500.00, 20, 
    (SELECT id_categoria FROM Categorias WHERE nombre_categoria='Tecnología' LIMIT 1));

INSERT INTO Categorias (nombre_categoria) VALUES ('Autoayuda') ON DUPLICATE KEY UPDATE id_categoria=id_categoria;
INSERT INTO Libros (titulo, autor, editorial, anio_publicacion, precio, stock_disponible, id_categoria) 
VALUES ('Romper el Círculo', 'Autor Desconocido', 'Editorial Desconocida', 2023, 280.00, 35, 
    (SELECT id_categoria FROM Categorias WHERE nombre_categoria='Autoayuda' LIMIT 1));

INSERT INTO Categorias (nombre_categoria) VALUES ('Terror') ON DUPLICATE KEY UPDATE id_categoria=id_categoria;
INSERT INTO Libros (titulo, autor, editorial, anio_publicacion, precio, stock_disponible, id_categoria) 
VALUES ('Si Te Gusta la Oscuridad', 'Autor Desconocido', 'Editorial Oscura', 2023, 320.00, 15, 
    (SELECT id_categoria FROM Categorias WHERE nombre_categoria='Terror' LIMIT 1));

INSERT INTO Categorias (nombre_categoria) VALUES ('Ciencia Ficción') ON DUPLICATE KEY UPDATE id_categoria=id_categoria;
INSERT INTO Libros (titulo, autor, editorial, anio_publicacion, precio, stock_disponible, id_categoria) 
VALUES ('Black Ping', 'Autor Desconocido', 'Editorial Desconocida', 2023, 400.00, 10, 
    (SELECT id_categoria FROM Categorias WHERE nombre_categoria='Ciencia Ficción' LIMIT 1));

INSERT INTO Categorias (nombre_categoria) VALUES ('Fantasía') ON DUPLICATE KEY UPDATE id_categoria=id_categoria;
INSERT INTO Libros (titulo, autor, editorial, anio_publicacion, precio, stock_disponible, id_categoria) 
VALUES ('Narnia: El León, la Bruja y el Armario', 'C.S. Lewis', 'Destino', 1950, 450.00, 60, 
    (SELECT id_categoria FROM Categorias WHERE nombre_categoria='Fantasía' LIMIT 1));

INSERT INTO Categorias (nombre_categoria) VALUES ('No Ficción') ON DUPLICATE KEY UPDATE id_categoria=id_categoria;
INSERT INTO Libros (titulo, autor, editorial, anio_publicacion, precio, stock_disponible, id_categoria) 
VALUES ('Vigilancia Permanente', 'Edward Snowden', 'Planeta', 2019, 370.00, 20, 
    (SELECT id_categoria FROM Categorias WHERE nombre_categoria='No Ficción' LIMIT 1));