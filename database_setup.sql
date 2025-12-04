-- Script SQL para inicializar la base de datos del proyecto Cosmitos Imperiales.
-- Este script se ejecuta automáticamente cuando el contenedor MySQL se inicia por primera vez.
-- La aplicación crea las tablas dinámicamente basadas en el nombre del archivo subido.

-- La base de datos ya se crea automáticamente por la variable MYSQL_DATABASE en docker-compose.yml
-- Solo necesitamos asegurarnos de que estamos usando la base de datos correcta
USE cosmitos_imperiales_db;

-- Crear una tabla de ejemplo para los resultados del análisis de sentimientos.
-- Nota: Esta es solo una estructura de tabla de ejemplo. La aplicación crea tablas
-- dinámicamente con nombres como 'analisis_<nombre_archivo>' cuando se procesan archivos.
CREATE TABLE IF NOT EXISTS analisis_sentimientos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    comentarios TEXT,
    calificacion FLOAT,
    Clasificacion VARCHAR(255)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS report_notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_name VARCHAR(255) NOT NULL,
    note_content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (analysis_name)
);
