# Panorama General

El Gestor de Satisfacción y Seguimiento de Posventa (GSSP) es una aplicación Streamlit para analizar comentarios de clientes mediante un modelo de sentimiento entrenado. Admite carga de archivos (Excel/CSV), limpieza automática de texto, clasificación, generación de resúmenes, exportes a Excel/PDF, envío de resultados por correo y mantenimiento de historiales.

## Características destacadas
- **Arquitectura limpia**: Separación clara entre dominio, casos de uso, adaptadores e infraestructura.
- **Persistencia dual**: Guarda análisis en CSV y MySQL, con soporte para consolidar o eliminar múltiples análisis desde la UI.
- **Visualización rica**: Gráficos de distribución, tablas filtrables, nubes de palabras y colores por clasificación.
- **Distribución de resultados**: Exportación a Excel/PDF y envío por correo electrónico con adjuntos.
- **Historial de reportes**: Registro en MySQL de reportes generados, con descarga y limpieza desde la interfaz.

## Flujo de usuario
1. Subir archivo desde la barra lateral.
2. El sistema limpia datos, ejecuta el modelo y guarda resultados.
3. En la vista principal se muestran gráficos, tablas y nubes de palabras.
4. El usuario puede exportar/descargar, enviar por email o guardar el reporte en historial.
5. Se pueden listar, consolidar o eliminar análisis previos y administrar el historial de reportes.

## Compatibilidad con Windows
- Probado con Python 3.8+ y Docker Desktop. Usa rutas relativas compatibles (CSV en `datos_analizados/`, reportes en `reports/`).
- Para activar el entorno en PowerShell: `.\.venv\Scripts\Activate.ps1`.
- Ejecuta `streamlit run src/app.py` tras configurar `.env` o las variables de entorno necesarias.
