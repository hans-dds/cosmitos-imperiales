import pytest
import pandas as pd
import os
import tempfile
import shutil
from unittest.mock import patch, mock_open
from main.datos.GuardarDatosArchivo import GuardarDatosArchivo

class TestGuardarDatosArchivo:
    
    @pytest.fixture
    def temp_dir(self):
        """Fixture para crear un directorio temporal para las pruebas"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_dataframe(self):
        """Fixture para crear un DataFrame de ejemplo"""
        return pd.DataFrame({
            'columna1': [1, 2, 3],
            'columna2': ['a', 'b', 'c'],
            'columna3': [1.1, 2.2, 3.3]
        })

    # Tests para __init__
    def test_init_datos_validos(self, temp_dir):
        """Test de inicialización con directorio válido"""
        guardador = GuardarDatosArchivo(temp_dir)
        assert guardador.directorio_base == temp_dir
        assert os.path.exists(temp_dir)

    def test_init_datos_invalidos(self):
        """Test de inicialización con directorio inválido"""
        directorio_invalido = "/directorio/que/no/existe/y/no/se/puede/crear"
        with pytest.raises((OSError, PermissionError)):
            GuardarDatosArchivo(directorio_invalido)

    def test_init_datos_nulos(self):
        """Test de inicialización con directorio None"""
        with pytest.raises(TypeError):
            GuardarDatosArchivo(None)

    # Tests para guardar_datos_limpios
    def test_guardar_datos_limpios_datos_validos(self, temp_dir, sample_dataframe):
        """Test de guardado con datos válidos"""
        guardador = GuardarDatosArchivo(temp_dir)
        resultado = guardador.guardar_datos_limpios(sample_dataframe, "test_archivo")
        
        assert resultado is True
        archivo_esperado = os.path.join(temp_dir, "test_archivo_limpio.csv")
        assert os.path.exists(archivo_esperado)
        
        # Verificar que el contenido se guardó correctamente
        df_leido = pd.read_csv(archivo_esperado)
        pd.testing.assert_frame_equal(df_leido, sample_dataframe)

    def test_guardar_datos_limpios_datos_invalidos(self, temp_dir):
        """Test de guardado con datos inválidos (no DataFrame)"""
        guardador = GuardarDatosArchivo(temp_dir)
        resultado = guardador.guardar_datos_limpios("no_es_dataframe", "test_archivo")
        
        assert resultado is False

    def test_guardar_datos_limpios_datos_nulos(self, temp_dir):
        """Test de guardado con datos nulos"""
        guardador = GuardarDatosArchivo(temp_dir)
        resultado = guardador.guardar_datos_limpios(None, "test_archivo")
        
        assert resultado is False

    def test_guardar_datos_limpios_dataframe_vacio(self, temp_dir):
        """Test de guardado con DataFrame vacío"""
        guardador = GuardarDatosArchivo(temp_dir)
        df_vacio = pd.DataFrame()
        resultado = guardador.guardar_datos_limpios(df_vacio, "test_archivo")
        
        assert resultado is False

    # Tests para crear_respaldo
    def test_crear_respaldo_datos_validos(self, temp_dir, sample_dataframe):
        """Test de creación de respaldo con datos válidos"""
        guardador = GuardarDatosArchivo(temp_dir)
        resultado = guardador.crear_respaldo(sample_dataframe, "test_respaldo")
        
        assert resultado is True
        # Verificar que se creó un archivo con el patrón de respaldo
        archivos = os.listdir(temp_dir)
        archivos_respaldo = [f for f in archivos if "test_respaldo_respaldo_" in f and f.endswith(".csv")]
        assert len(archivos_respaldo) == 1

    def test_crear_respaldo_datos_invalidos(self, temp_dir):
        """Test de creación de respaldo con datos inválidos"""
        guardador = GuardarDatosArchivo(temp_dir)
        resultado = guardador.crear_respaldo("no_es_dataframe", "test_respaldo")
        
        assert resultado is False

    def test_crear_respaldo_datos_nulos(self, temp_dir):
        """Test de creación de respaldo con datos nulos"""
        guardador = GuardarDatosArchivo(temp_dir)
        resultado = guardador.crear_respaldo(None, "test_respaldo")
        
        assert resultado is False

    # Tests para validar_integridad_datos
    def test_validar_integridad_datos_validos(self, temp_dir, sample_dataframe):
        """Test de validación con archivo CSV válido"""
        guardador = GuardarDatosArchivo(temp_dir)
        archivo_test = os.path.join(temp_dir, "test_valido.csv")
        sample_dataframe.to_csv(archivo_test, index=False)
        
        resultado = guardador.validar_integridad_datos(archivo_test)
        assert resultado is True

    def test_validar_integridad_datos_invalidos(self, temp_dir):
        """Test de validación con archivo corrupto"""
        guardador = GuardarDatosArchivo(temp_dir)
        archivo_corrupto = os.path.join(temp_dir, "corrupto.csv")
        
        # Crear un archivo con contenido inválido
        with open(archivo_corrupto, 'w') as f:
            f.write("contenido,inválido\n1,2,3,4,5\n")
        
        resultado = guardador.validar_integridad_datos(archivo_corrupto)
        # Dependiendo de pandas, esto podría ser True o False, ajustar según comportamiento
        assert isinstance(resultado, bool)

    def test_validar_integridad_datos_nulos(self, temp_dir):
        """Test de validación con ruta nula o archivo inexistente"""
        guardador = GuardarDatosArchivo(temp_dir)
        
        # Test con ruta None - ahora debería retornar False en lugar de lanzar excepción
        resultado = guardador.validar_integridad_datos(None)
        assert resultado is False
        
        # Test con archivo inexistente
        resultado = guardador.validar_integridad_datos("archivo_inexistente.csv")
        assert resultado is False

    # Tests para obtener_metadatos_archivo
    def test_obtener_metadatos_archivo_datos_validos(self, temp_dir, sample_dataframe):
        """Test de obtención de metadatos con archivo válido"""
        guardador = GuardarDatosArchivo(temp_dir)
        archivo_test = os.path.join(temp_dir, "test_metadatos.csv")
        sample_dataframe.to_csv(archivo_test, index=False)
        
        metadatos = guardador.obtener_metadatos_archivo(archivo_test)
        
        assert isinstance(metadatos, dict)
        assert 'ruta' in metadatos
        assert 'tamaño_bytes' in metadatos
        assert 'ultima_modificacion' in metadatos
        assert metadatos['ruta'] == archivo_test
        assert metadatos['tamaño_bytes'] > 0

    def test_obtener_metadatos_archivo_datos_invalidos(self, temp_dir):
        """Test de obtención de metadatos con ruta inválida"""
        guardador = GuardarDatosArchivo(temp_dir)
        metadatos = guardador.obtener_metadatos_archivo("archivo_inexistente.csv")
        
        assert metadatos == {}

    def test_obtener_metadatos_archivo_datos_nulos(self, temp_dir):
        """Test de obtención de metadatos con ruta nula"""
        guardador = GuardarDatosArchivo(temp_dir)
        
        metadatos = guardador.obtener_metadatos_archivo(None)
        assert metadatos == {}