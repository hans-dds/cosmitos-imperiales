CREATE DATABASE IF NOT EXISTS cosmitos_imperiales_db;

USE cosmitos_imperiales_db;

CREATE TABLE IF NOT EXISTS analisis_sentimientos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    comentarios TEXT,
    calificacion FLOAT,
    Clasificacion VARCHAR(255)
);
