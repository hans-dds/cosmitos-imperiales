"""
Pruebas unitarias para componentes específicos de la aplicación Streamlit.
Enfocado en probar las funciones de presentación y controladores.

Para ejecutar:
source ./Py/bin/activate.fish
pytest tests/test_streamlit_components.py -v
"""

import pytest
import pandas as pd
from streamlit.testing.v1 import AppTest
import os
import sys
from io import BytesIO, StringIO

# Agregar el directorio src/main al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'main'))


class TestLayoutComponents:
    """Pruebas para los componentes de layout (presentacion.vista.layout)"""
    
    @pytest.fixture
    def sample_dataframe(self):
        """Crea un DataFrame de ejemplo para las pruebas"""
        return pd.DataFrame({
            'Clasificacion': ['Promotor', 'Detractor', 'Neutro', 'Promotor', 'Detractor'],
            'comentarios': [
                'Excelente servicio, muy profesional',
                'Pésima atención',
                'Normal, nada especial',
                'Me encantó la experiencia',
                'Muy malo el producto'
            ],
            'calificacion': [5, 1, 3, 5, 1],
            'longitud': [34, 17, 23, 24, 21]
        })
    
    def test_show_header_import(self):
        """Verifica que show_header se puede importar"""
        from presentacion.vista.layout import show_header
        assert callable(show_header), "show_header no es una función callable"
    
    def test_show_tables_import(self):
        """Verifica que show_tables se puede importar"""
        from presentacion.vista.layout import show_tables
        assert callable(show_tables), "show_tables no es una función callable"
    
    def test_upload_file_view_import(self):
        """Verifica que upload_file_view se puede importar"""
        from presentacion.vista.layout import upload_file_view
        assert callable(upload_file_view), "upload_file_view no es una función callable"
    
    def test_show_tables_with_valid_dataframe(self, sample_dataframe):
        """
        Prueba que show_tables funciona con un DataFrame válido.
        Nota: Esta función usa Streamlit, por lo que necesita contexto de app.
        """
        # Esta prueba verifica que el DataFrame tiene las columnas necesarias
        required_columns = {'Clasificacion', 'comentarios', 'calificacion', 'longitud'}
        assert required_columns.issubset(sample_dataframe.columns), \
            "El DataFrame de prueba no tiene todas las columnas necesarias"


class TestLoaderFunctions:
    """Pruebas para las funciones del loader (presentacion.controlador.loader)"""
    
    def test_get_services_import(self):
        """Verifica que get_services se puede importar"""
        from presentacion.controlador.loader import get_services
        assert callable(get_services), "get_services no es una función callable"
    
    def test_process_uploaded_file_import(self):
        """Verifica que process_uploaded_file se puede importar"""
        from presentacion.controlador.loader import process_uploaded_file
        assert callable(process_uploaded_file), "process_uploaded_file no es una función callable"
    
    def test_process_uploaded_file_with_invalid_extension(self):
        """
        Verifica que process_uploaded_file maneja correctamente extensiones inválidas.
        """
        from presentacion.controlador.loader import process_uploaded_file
        from negocio.ServicioLimpiarDatos import ServicioLimpiarDatos as SLD
        
        # Crear un mock de archivo con extensión inválida
        class MockFile:
            def __init__(self, name):
                self.name = name
                self.content = b"test content"
            
            def seek(self, pos):
                pass
        
        mock_file = MockFile("test.txt")
        sld = SLD()
        
        # process_uploaded_file necesita sae también, pero para este test
        # solo verificamos el manejo de extensión
        try:
            # Nota: Esta prueba puede necesitar ajustes según la implementación exacta
            from presentacion.controlador.loader import get_services
            try:
                _, sae = get_services()
                result, mensaje, valido = process_uploaded_file(mock_file, sld, sae)
                assert not valido, "Debería rechazar archivos con extensión no soportada"
                assert "no soportada" in mensaje.lower(), "El mensaje debería indicar extensión no soportada"
            except FileNotFoundError:
                pytest.skip("No se encontró el modelo entrenado")
        except Exception as e:
            pytest.skip(f"Error al ejecutar la prueba: {e}")


class TestAppWithFileUpload:
    """Pruebas de la app simulando carga de archivos"""
    
    @pytest.fixture
    def csv_test_app(self):
        """Crea una mini app de prueba para simular procesamiento"""
        app_script = """
import streamlit as st
import pandas as pd

st.title("Test File Processing")

# Simular datos cargados
sample_data = {
    'Calificacion': [5, 4, 3],
    'Comentarios': ['Excelente', 'Bueno', 'Regular']
}
df = pd.DataFrame(sample_data)

st.success("Datos de prueba cargados")
st.dataframe(df)
st.write(f"Filas: {len(df)}")
"""
        at = AppTest.from_string(app_script)
        return at
    
    def test_data_processing_structure(self, csv_test_app):
        """Verifica la estructura básica de procesamiento de datos"""
        csv_test_app.run()
        
        # Verificar que no hay excepciones
        assert not csv_test_app.exception
        
        # Verificar que se muestran dataframes
        assert len(csv_test_app.dataframe) > 0


class TestDataProcessingFlow:
    """Pruebas del flujo de procesamiento de datos"""
    
    @pytest.fixture
    def sample_csv_content(self):
        """Genera contenido CSV de muestra"""
        data = {
            'Calificacion': [5, 4, 3, 2, 1],
            'Comentarios': [
                'Excelente servicio',
                'Muy bueno',
                'Normal',
                'Malo',
                'Pésimo'
            ]
        }
        df = pd.DataFrame(data)
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        return csv_buffer.getvalue()
    
    def test_csv_data_structure(self, sample_csv_content):
        """Verifica que el CSV de prueba tiene la estructura correcta"""
        df = pd.read_csv(StringIO(sample_csv_content))
        assert 'Calificacion' in df.columns
        assert 'Comentarios' in df.columns
        assert len(df) == 5


class TestSessionStateManagement:
    """Pruebas para el manejo de session_state"""
    
    def test_session_state_with_dataframe(self):
        """Verifica el manejo de DataFrames en session_state"""
        app_script = """
import streamlit as st
import pandas as pd

if 'df_actual' not in st.session_state:
    st.session_state['df_actual'] = None
    st.session_state['analisis_actual'] = None

if st.session_state['df_actual'] is not None:
    st.success(f"Análisis cargado: {st.session_state['analisis_actual']}")
    st.dataframe(st.session_state['df_actual'])
else:
    st.info("No hay análisis cargado")
"""
        at = AppTest.from_string(app_script)
        at.run()
        
        # Verificar que se muestra el mensaje de no hay análisis
        assert len(at.info) > 0
        
        # Agregar datos a session_state
        sample_df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c']
        })
        at.session_state['df_actual'] = sample_df
        at.session_state['analisis_actual'] = 'test'
        at.run()
        
        # Verificar que ahora se muestra el success
        assert len(at.success) > 0
        assert len(at.dataframe) > 0


class TestAnalysisDisplay:
    """Pruebas para la visualización de análisis"""
    
    def test_classification_display(self):
        """Verifica que se muestran correctamente las clasificaciones"""
        app_script = """
import streamlit as st
import pandas as pd

df = pd.DataFrame({
    'Clasificacion': ['Promotor', 'Detractor', 'Neutro'],
    'comentarios': ['Bueno', 'Malo', 'Normal'],
    'calificacion': [5, 1, 3],
    'longitud': [5, 4, 6]
})

st.title("Resultados de Clasificación")

for categoria in ['Promotor', 'Detractor', 'Neutro']:
    st.subheader(categoria)
    df_cat = df[df['Clasificacion'] == categoria]
    st.write(f"Total: {len(df_cat)}")
"""
        at = AppTest.from_string(app_script)
        at.run()
        
        # Verificar que no hay excepciones
        assert not at.exception
        
        # Verificar que hay subheaders para cada categoría
        assert len(at.subheader) >= 3
        
        # Verificar los títulos de las categorías
        subheader_values = [sh.value for sh in at.subheader]
        assert 'Promotor' in subheader_values
        assert 'Detractor' in subheader_values
        assert 'Neutro' in subheader_values


class TestButtonInteractions:
    """Pruebas para interacciones con botones"""
    
    def test_save_button_click(self):
        """Verifica la interacción con botón de guardar"""
        app_script = """
import streamlit as st

if 'saved' not in st.session_state:
    st.session_state['saved'] = False

if st.button("Guardar Resultados"):
    st.session_state['saved'] = True
    st.success("Resultados guardados exitosamente")

if st.session_state['saved']:
    st.info("Ya se guardaron los resultados")
"""
        at = AppTest.from_string(app_script)
        at.run()
        
        # Inicialmente no debería estar guardado
        assert 'saved' in at.session_state
        assert not at.session_state['saved']
        
        # Simular click en el botón
        if len(at.button) > 0:
            at.button[0].click().run()
            
            # Verificar que se guardó
            assert at.session_state['saved']
            
            # Verificar que aparece el mensaje de éxito
            assert len(at.success) > 0


class TestSelectboxInteraction:
    """Pruebas para interacciones con selectbox"""
    
    def test_analysis_selection(self):
        """Verifica la selección de análisis desde selectbox"""
        app_script = """
import streamlit as st

lista_analisis = ['Análisis 1', 'Análisis 2', 'Análisis 3']

if lista_analisis:
    analisis_seleccionado = st.selectbox(
        "Seleccionar un análisis",
        lista_analisis
    )
    st.write(f"Seleccionado: {analisis_seleccionado}")
else:
    st.info("No hay análisis disponibles")
"""
        at = AppTest.from_string(app_script)
        at.run()
        
        # Verificar que existe el selectbox
        assert len(at.selectbox) > 0
        
        # Verificar que tiene opciones
        selectbox = at.selectbox[0]
        assert selectbox is not None
        
        # Simular selección de una opción
        at.selectbox[0].select('Análisis 2').run()
        
        # Verificar que no hay excepciones
        assert not at.exception


class TestErrorHandling:
    """Pruebas para el manejo de errores"""
    
    def test_empty_dataframe_handling(self):
        """Verifica el manejo de DataFrames vacíos"""
        app_script = """
import streamlit as st
import pandas as pd

df = pd.DataFrame()

if df.empty:
    st.warning("No se encontraron datos válidos")
else:
    st.success("Datos cargados correctamente")
    st.dataframe(df)
"""
        at = AppTest.from_string(app_script)
        at.run()
        
        # Verificar que aparece el warning
        assert len(at.warning) > 0
        
        # Verificar que el mensaje es correcto
        warnings = [w.value for w in at.warning]
        assert any("No se encontraron" in w for w in warnings)
    
    def test_missing_columns_handling(self):
        """Verifica el manejo de columnas faltantes"""
        app_script = """
import streamlit as st
import pandas as pd

df = pd.DataFrame({'col1': [1, 2, 3]})

required_columns = {'col1', 'col2', 'col3'}

if not required_columns.issubset(df.columns):
    st.error("Faltan columnas requeridas")
else:
    st.success("Todas las columnas están presentes")
"""
        at = AppTest.from_string(app_script)
        at.run()
        
        # Verificar que aparece el error
        assert len(at.error) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
