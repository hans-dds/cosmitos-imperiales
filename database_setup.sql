-- Este script SQL es un ejemplo de esquema para la base de datos.
-- La aplicación crea las tablas dinámicamente, por lo que este script es solo una guía.

-- Script SQL para crear la base de datos y una tabla de ejemplo para el proyecto Cosmitos Imperiales.

-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS cosmitos_imperiales_db;

-- Usar la base de datos creada
USE cosmitos_imperiales_db;

-- Crear una tabla de ejemplo para los resultados del análisis de sentimientos.
-- Nota: La aplicación crea tablas dinámicamente basadas en el nombre del archivo subido.
-- Esta es solo una estructura de tabla de ejemplo.
CREATE TABLE IF NOT EXISTS analisis_sentimientos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    comentarios TEXT,
    calificacion FLOAT,
    Clasificacion VARCHAR(255)
);

-- Se pueden crear más tablas con la misma estructura pero con diferentes nombres según sea necesario.
-- Por ejemplo, si se sube un archivo llamado 'reporte_mayo.csv', la aplicación
-- creará una tabla llamada 'analisis_reporte_mayo'.
