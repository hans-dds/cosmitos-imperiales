# Pruebas Unitarias - Aplicación de Clasificación de Comentarios

Este directorio contiene las pruebas unitarias para la aplicación de Streamlit que clasifica comentarios de negocios en Detractores, Promotores y Neutros.

## 📁 Estructura de Pruebas

```
tests/
├── test_streamlit_app.py          # Pruebas principales de la aplicación
├── test_streamlit_components.py   # Pruebas de componentes específicos
├── test_almacenamiento.py         # Pruebas existentes de almacenamiento
├── test_analisis_evaluacion.py   # Pruebas existentes de análisis
└── Pruebas-Unitarias-README.md                 # Este archivo
```

## 🧪 Archivos de Prueba

### `test_streamlit_app.py`
Pruebas principales de la aplicación Streamlit:
- ✅ Carga correcta de la aplicación
- ✅ Existencia de componentes UI (títulos, sidebar, etc.)
- ✅ Funcionalidad del file uploader
- ✅ Manejo de session_state
- ✅ Visualización de análisis cargados
- ✅ Interacciones con botones y selectbox

**Clases de prueba:**
- `TestStreamlitApp`: Pruebas básicas de la aplicación
- `TestAppWithMockedData`: Pruebas con datos simulados
- `TestAppComponents`: Pruebas de componentes importados
- `TestAppInteractions`: Pruebas de interacciones de usuario
- `TestAppIntegration`: Pruebas de integración completa

### `test_streamlit_components.py`
Pruebas de componentes específicos:
- ✅ Funciones de layout (show_header, show_tables, upload_file_view)
- ✅ Funciones del controlador (get_services, process_uploaded_file)
- ✅ Procesamiento de archivos CSV
- ✅ Manejo de session_state
- ✅ Visualización de clasificaciones
- ✅ Manejo de errores

**Clases de prueba:**
- `TestLayoutComponents`: Componentes de presentación
- `TestLoaderFunctions`: Funciones del cargador
- `TestSessionStateManagement`: Gestión del estado
- `TestAnalysisDisplay`: Visualización de análisis
- `TestButtonInteractions`: Interacciones con botones
- `TestSelectboxInteraction`: Interacciones con selectbox
- `TestErrorHandling`: Manejo de errores

## 🚀 Cómo Ejecutar las Pruebas

### 1. Activar el Entorno Virtual

```fish
source ./Py/bin/activate
```

### 2. Ejecutar Todas las Pruebas

```fish
# Todas las pruebas de Streamlit
pytest tests/test_streamlit_app.py tests/test_streamlit_components.py -v

# Solo pruebas principales
pytest tests/test_streamlit_app.py -v

# Solo pruebas de componentes
pytest tests/test_streamlit_components.py -v
```

### 3. Ejecutar Pruebas Específicas

```fish
# Una clase de pruebas específica
pytest tests/test_streamlit_app.py::TestStreamlitApp -v

# Una prueba específica
pytest tests/test_streamlit_app.py::TestStreamlitApp::test_app_loads_successfully -v
```

### 4. Ejecutar con Cobertura

```fish
# Generar reporte de cobertura
pytest tests/test_streamlit_app.py tests/test_streamlit_components.py --cov=src/main --cov-report=html

# Ver reporte en el navegador
# El reporte se genera en htmlcov/index.html
```

### 5. Ejecutar con Diferentes Niveles de Verbosidad

```fish
# Modo silencioso (solo resultados)
pytest tests/test_streamlit_app.py -q

# Modo normal
pytest tests/test_streamlit_app.py

# Modo verbose (muestra cada test)
pytest tests/test_streamlit_app.py -v

# Modo muy verbose (muestra detalles completos)
pytest tests/test_streamlit_app.py -vv
```

## 📊 Opciones Útiles de Pytest

```fish
# Detener en el primer fallo
pytest tests/test_streamlit_app.py -x

# Mostrar variables locales en errores
pytest tests/test_streamlit_app.py -l

# Mostrar print statements
pytest tests/test_streamlit_app.py -s

# Ejecutar solo tests que fallaron la última vez
pytest tests/test_streamlit_app.py --lf

# Ejecutar tests en paralelo (requiere pytest-xdist)
pytest tests/test_streamlit_app.py -n auto
```

## 🔧 Configuración

Las pruebas utilizan la configuración definida en `pytest.ini`:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

## 📝 Notas Importantes

### Limitaciones Conocidas

1. **Modelo de ML**: Algunas pruebas pueden fallar si el archivo del modelo (`clasificador_sentimiento_final.pkl`) no existe. Estas pruebas se saltarán automáticamente con `pytest.skip()`.

2. **Base de Datos**: Las pruebas que interactúan con la base de datos pueden requerir configuración adicional o datos de prueba.

3. **File Upload**: La funcionalidad completa de carga de archivos tiene limitaciones en el entorno de testing de Streamlit.

### Pruebas que Pueden Requerir Datos Externos

- `test_get_services_function`: Requiere el modelo ML
- `test_sidebar_analysis_list`: Depende de análisis guardados en BD
- `test_file_uploader_accepts_csv`: Requiere procesamiento completo

### Datos de Prueba

Los tests crean datos de ejemplo internamente:

```python
sample_data = pd.DataFrame({
    'Calificacion': [5, 4, 3, 2, 1],
    'Comentarios': [
        'Excelente servicio',
        'Buen producto',
        'Normal',
        'Malo',
        'Pésimo'
    ]
})
```

## 🐛 Depuración de Pruebas

### Ver trazas completas de errores

```fish
pytest tests/test_streamlit_app.py --tb=long
```

### Usar debugger en una prueba

```python
def test_example(self, app):
    import pdb; pdb.set_trace()
    app.run()
    assert not app.exception
```

### Ver warnings

```fish
pytest tests/test_streamlit_app.py -W all
```

## 📈 Mejores Prácticas

1. **Ejecutar pruebas antes de commit**: Asegúrate de que todas las pruebas pasen antes de hacer commit.

2. **Mantener pruebas aisladas**: Cada prueba debe ser independiente y no depender del estado de otras.

3. **Usar fixtures**: Reutiliza configuración común a través de fixtures de pytest.

4. **Nombres descriptivos**: Los nombres de las pruebas deben describir claramente qué están probando.

5. **Documentación**: Documenta pruebas complejas con docstrings.

## 🔄 Integración Continua

Estas pruebas pueden integrarse en un pipeline CI/CD:

```yaml
# Ejemplo para GitHub Actions
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest tests/test_streamlit_app.py tests/test_streamlit_components.py -v
```

## 📚 Recursos Adicionales

- [Documentación oficial de Streamlit Testing](https://docs.streamlit.io/develop/api-reference/app-testing)
- [Documentación de Pytest](https://docs.pytest.org/)
- [AppTest API Reference](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest)

## 🆘 Solución de Problemas

### Error: "No module named 'streamlit.testing'"

Asegúrate de tener Streamlit 1.18.0 o superior:

```fish
pip install --upgrade streamlit
```

### Error: "AppTest timeout"

Aumenta el timeout en el fixture:

```python
at = AppTest.from_file(app_path, default_timeout=30)
```

### Error: "FileNotFoundError: modelo no encontrado"

Algunas pruebas se saltarán automáticamente. Esto es esperado si no tienes el modelo entrenado.

---

**Última actualización**: Noviembre 2025
**Versión de Streamlit requerida**: 1.50.0+
**Versión de Python**: 3.13+
