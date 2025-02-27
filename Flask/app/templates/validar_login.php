<?php

$usuario = $_POST['admin'];
$clave = $_POST['admin123'];  // Asegúrate de que coincida con el nombre del campo en tu formulario HTML

$conexion = mysqli_connect("localhost", "admin", "admin123", "validacion");

// Verificar la conexión
if (mysqli_connect_errno()) {
    echo "Error al conectar a la base de datos: " . mysqli_connect_error();
    exit();
}

$consulta = "SELECT * FROM usuarios WHERE usuario='$usuario' and clave='$clave'";
$resultado = mysqli_query($conexion, $consulta);

$filas = mysqli_num_rows($resultado);

if ($filas > 0) {
    header("location:index2.php");
} else {
    echo "Error en la autenticación";
}

mysqli_free_result($resultado);
mysqli_close($conexion);
?>
