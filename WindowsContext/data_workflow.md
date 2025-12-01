# Flujo de Datos

## 1. Ingesta
- El usuario carga un archivo desde la barra lateral (Excel/CSV). `PandasFileReader` valida hojas requeridas (`EXCEL_REQUIRED_SHEETS`) y devuelve un `DataFrame` crudo.
- El nombre base del archivo (ej. `c_Abril_2025`) se usa para nombrar tablas y derivar mes/año si no hay columna de fecha.

## 2. Limpieza y preparación
- `PandasDataCleaner` normaliza columnas (`calificacion`, `comentarios`, `fecha`), convierte calificaciones a enteros y ejecuta limpieza de texto (`domain.services.text_cleaner.clean_text`).
- Se eliminan comentarios irrelevantes con `filter_irrelevant_comments` y se descartan filas vacías.

## 3. Análisis de sentimiento
- `JoblibSentimentAnalyzer` aplica el modelo `clasificador_sentimiento_final.pkl` para asignar `Clasificacion` y `Fiabilidad` a cada comentario.
- `ProcessFileUseCase` agrega `fecha` derivada del nombre del archivo si no existe, permitiendo filtros temporales posteriores.

## 4. Persistencia
- Los resultados analizados se guardan en:
  - CSV en `CSV_BASE_DIR` (`{analysis_id}_limpio.csv`).
  - MySQL en tablas `analisis_{analysis_id}` con columnas `comentarios`, `calificacion`, `Clasificacion`, `Fiabilidad` y `fecha` opcional.

## 5. Visualización y resumen
- `StreamlitController.prepare_analysis_display` agrega colores por clasificación y secciones de gráficos/tablas.
- `GenerateSummaryUseCase` calcula distribución, porcentajes y longitud promedio de comentarios para alimentar gráficos.
- Componentes UI (`charts_component`, `table_component`, `word_cloud_component`) presentan anillos, barras, tablas y nubes de palabras.

## 6. Exportación y distribución
- **Excel**: `infrastructure/ui/export.py` genera un archivo con hojas `Datos` y `Resumen` más gráficas incrustadas.
- **PDF**: `export_pdf.py` permite reportes en PDF usando el color map calculado.
- **Correo**: `SendResultsEmailUseCase` usa `SmtpEmailSender` para adjuntar Excel o PDF y enviar resultados.

## 7. Historial y mantenimiento
- `SaveReportUseCase` almacena metadatos de reportes en `report_history` via `SQLReportRepository` y guarda archivos bajo `reports/`.
- `ListReportsUseCase`, `ClearReportsHistoryUseCase` y `DeleteReportUseCase` permiten consultar y limpiar historial desde la UI.
- Eliminación de análisis individuales o múltiples se gestiona con `DeleteAnalysisUseCase`, incluyendo limpieza de tablas MySQL y CSV asociados.
