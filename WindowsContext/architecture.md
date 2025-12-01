# Arquitectura del Gestor de Satisfacción y Seguimiento de Posventa (GSSP)

## Vista general
El proyecto sigue principios de Arquitectura Limpia para separar reglas de negocio, lógica de aplicación, adaptadores y detalles de infraestructura. La UI está construida en Streamlit y usa un contenedor de dependencias para ensamblar adaptadores (lectura de archivos, limpieza, análisis de sentimientos, persistencia en MySQL/CSV, envío de correos y repositorio de reportes).

## Capas y dependencias
- **Dominio (`src/domain`)**: Entidades y servicios puros para limpieza de texto, filtrado de comentarios irrelevantes, cálculo de métricas y preparación de corpus de nubes de palabras.
- **Casos de uso (`src/use_cases`)**: Orquestan acciones como lectura de archivos, procesamiento y análisis, carga/listado/eliminación de análisis, generación de resúmenes, exportación y envío de resultados por email, y gestión de historial de reportes.
- **Adaptadores (`src/adapters`)**: Implementaciones concretas de puertos, incluyendo `PandasFileReader`, `PandasDataCleaner`, `JoblibSentimentAnalyzer`, `SQLandCSVAnalysisRepository`, `SQLReportRepository` y `SmtpEmailSender`.
- **Infraestructura (`src/infrastructure`)**: Configuración de entorno, contenedor de inyección de dependencias y capa de UI (componentes Streamlit para carga de archivos, gráficos, tablas, exportaciones y gestión de reportes).

Las dependencias apuntan hacia adentro (Infraestructura → Adaptadores → Casos de uso → Dominio). Los casos de uso dependen de puertos definidos en `use_cases/ports` y el contenedor (`infrastructure/dependency_injection_container.py`) enlaza implementaciones concretas.

## Componentes clave
- **Procesamiento**: `ProcessFileUseCase` limpia datos con `PandasDataCleaner`, ejecuta el modelo de sentimientos (`JoblibSentimentAnalyzer`) y persiste resultados via `SQLandCSVAnalysisRepository`.
- **Persistencia**: Los análisis se guardan tanto en CSV como en tablas MySQL prefijadas con `analisis_`; los reportes PDF/Excel se registran en `report_history` usando `SQLReportRepository`.
- **UI**: `StreamlitController` expone métodos para cargar/borrar análisis, preparar visualizaciones, enviar correos, generar/exportar reportes y descargar historial. Componentes en `infrastructure/ui/components` renderizan sidebar, contenido principal, gráficos, tablas, exportes y gestión de reportes.
- **Integraciones**: Modelo de sentimiento empaquetado en `src/infrastructure/ML/clasificador_sentimiento_final.pkl`; SMTP configurable para envío de resultados; almacenamiento de reportes en disco bajo `reports/`.

## Consideraciones de Windows
- El proyecto puede ejecutarse en Windows con Python 3.8+ y Docker Desktop. Las rutas relativas (CSV en `datos_analizados/` y reportes en `reports/`) funcionan tanto en WSL como en entornos nativos.
- Las dependencias se cargan desde `.env`; en PowerShell, usa `python -m venv .venv` y `.\.venv\Scripts\Activate.ps1` antes de `pip install -e .`.
- Si se usa Docker Compose en Windows, asegúrate de que el puerto MySQL (por defecto 3306) no esté ocupado y que los volúmenes se creen con permisos de escritura para la carpeta del proyecto.
