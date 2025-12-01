# Módulos Principales

## Dominio (`src/domain`)
- `entities/review.py`: Entidades `Review` y `AnalyzedReview` para comentarios y resultados.
- `value_objects/sentiment.py`: Enum `Sentiment` con conversión numérica/string.
- `services/`: Servicios puros para limpieza de texto, filtrado, métricas, fiabilidad y corpus de nubes de palabras.

## Casos de uso (`src/use_cases`)
- **Ingesta y análisis**: `ReadFileUseCase`, `ProcessFileUseCase`.
- **Gestión de análisis**: `LoadAnalysisUseCase`, `ListAnalysesUseCase`, `DeleteAnalysisUseCase` (incluye eliminación múltiple), `PrepareAnalysisDisplayUseCase`.
- **Resumen y exportes**: `GenerateSummaryUseCase`, `SendResultsEmailUseCase` (correo con adjuntos), `SaveReportUseCase`, `ListReportsUseCase`, `ClearReportsHistoryUseCase`, `DeleteReportUseCase`.

## Adaptadores (`src/adapters`)
- `file_readers/PandasFileReader`: Lee Excel/CSV y valida hojas requeridas.
- `data_cleaner_adapter.PandasDataCleaner`: Normaliza columnas, limpia texto y filtra irrelevantes.
- `sentiment_analyzer_adapter.JoblibSentimentAnalyzer`: Carga modelo Joblib y asigna clasificación/fiabilidad.
- `repositories/SQLandCSVAnalysisRepository`: Persiste análisis en CSV y MySQL; soporta carga/listado/eliminación múltiple.
- `repositories/SQLReportRepository`: Historial de reportes (metadata en MySQL y archivos en disco).
- `email_sender_adapter.SmtpEmailSender`: Envío SMTP configurable.

## Infraestructura y UI (`src/infrastructure`)
- `config.py`: Lee variables de entorno y define `settings` compartidos.
- `dependency_injection_container.py`: Ensambla adaptadores y casos de uso; expone `container.streamlit_controller`.
- `ui/`: Configuración de página, constantes, exportadores (Excel/PDF), tablas y gráficos.
- `ui/components/`: Componentes Streamlit (sidebar, carga de archivos, tablas, gráficos, nubes de palabras, exportaciones y gestion de historial de reportes).
- `ui/controllers/streamlit_controller.py`: Puente entre UI y casos de uso para flujos de carga, análisis, exportes y mantenimiento.

## Scripts auxiliares
- `mock_smtp_server.py`: Servidor SMTP de pruebas.
- `debug_eml_generation.py`: Utilidad para depurar generación de EML.
- `database_setup.sql`: Script de inicialización de MySQL ejecutado por Docker Compose.
