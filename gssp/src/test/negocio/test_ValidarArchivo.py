import pytest
import pandas as pd
from io import BytesIO
from unittest.mock import patch, MagicMock
from main.negocio.ServicioValidarArchivo import ServicioValidarArchivo

class TestServicioValidarArchivo:
    
    def setup_method(self):
        """Setup para cada test"""
        self.servicio = ServicioValidarArchivo()
    
    @pytest.fixture
    def df_valido(self):
        """DataFrame con datos válidos"""
        return pd.DataFrame({
            'Calificacion': [5, 4, 3, 2, 1],
            'Comentarios': ['Excelente servicio', 'Muy bueno', 'Regular atención', 'Malo el trato', 'Pésimo servicio']
        })
    
    @pytest.fixture
    def archivo_excel_valido_stream(self, df_valido):
        """Stream de archivo Excel válido en memoria"""
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_valido.to_excel(writer, sheet_name='ATC', index=False)
            df_valido.to_excel(writer, sheet_name='Encuesta salida', index=False)
        buffer.seek(0)
        return buffer
    
    @pytest.fixture
    def archivo_excel_invalido_stream(self, df_valido):
        """Stream de archivo Excel con estructura inválida"""
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_valido.to_excel(writer, sheet_name='HojaIncorrecta', index=False)
        buffer.seek(0)
        return buffer
    
    @pytest.fixture
    def archivo_texto_stream(self):
        """Stream de archivo de texto (no Excel)"""
        buffer = BytesIO()
        buffer.write(b"Este es un archivo de texto, no Excel")
        buffer.seek(0)
        return buffer
    
    # Tests para leer_archivo
    def test_leer_archivo_datos_validos(self, archivo_excel_valido_stream):
        """Test con archivo Excel válido"""
        resultado, mensaje = self.servicio.leer_archivo(archivo_excel_valido_stream, "archivo_valido.xlsx")
        
        assert resultado is True
        assert mensaje is None
        assert self.servicio.obtener_datos_archivo() is not None
    
    def test_leer_archivo_datos_invalidos(self, archivo_texto_stream):
        """Test con archivo con extensión inválida"""
        resultado, mensaje = self.servicio.leer_archivo(archivo_texto_stream, "archivo.txt")
        
        assert resultado is False
        assert "Extensión inválida" in mensaje
        assert self.servicio.obtener_datos_archivo() is None
    
    def test_leer_archivo_datos_nulos(self):
        """Test con datos nulos o vacíos"""
        # Test con BytesIO vacío
        buffer_vacio = BytesIO()
        resultado, mensaje = self.servicio.leer_archivo(buffer_vacio, "archivo.xlsx")
        
        assert resultado is False
        assert mensaje is not None
        
        # Test con nombre de archivo vacío
        buffer = BytesIO(b"contenido")
        resultado, mensaje = self.servicio.leer_archivo(buffer, "")
        
        assert resultado is False
        assert "Extensión inválida" in mensaje
    
    # Tests para _leer_datos_excel
    def test_leer_datos_excel_datos_validos(self, archivo_excel_valido_stream):
        """Test con stream Excel válido"""
        resultado = self.servicio._leer_datos_excel(archivo_excel_valido_stream, "xlsx")
        
        assert resultado is not None
        assert isinstance(resultado, dict)
        assert 'ATC' in resultado
        assert 'Encuesta salida' in resultado
    
    def test_leer_datos_excel_datos_invalidos(self, archivo_texto_stream):
        """Test con stream que no es Excel válido"""
        resultado = self.servicio._leer_datos_excel(archivo_texto_stream, "xlsx")
        
        assert resultado is None
    
    def test_leer_datos_excel_datos_nulos(self):
        """Test con stream nulo o extensión inválida"""
        buffer_vacio = BytesIO()
        resultado = self.servicio._leer_datos_excel(buffer_vacio, "xlsx")
        
        assert resultado is None
        
        # Test con extensión no soportada
        buffer = BytesIO(b"contenido")
        resultado = self.servicio._leer_datos_excel(buffer, "pdf")
        
        assert resultado is None
    
    # Tests para _validar_estructura
    def test_validar_estructura_datos_validos(self, df_valido):
        """Test con estructura válida"""
        datos_validos = {
            'ATC': df_valido,
            'Encuesta salida': df_valido
        }
        
        resultado, mensaje = self.servicio._validar_estructura(datos_validos)
        
        assert resultado is True
        assert mensaje is None
    
    def test_validar_estructura_datos_invalidos(self, df_valido):
        """Test con estructura inválida"""
        # Test con hojas incorrectas
        datos_invalidos = {
            'HojaIncorrecta1': df_valido,
            'HojaIncorrecta2': df_valido
        }
        
        resultado, mensaje = self.servicio._validar_estructura(datos_invalidos)
        
        assert resultado is False
        assert "debe contener una hoja llamada 'ATC'" in mensaje
        
        # Test con número incorrecto de hojas
        datos_una_hoja = {'ATC': df_valido}
        resultado, mensaje = self.servicio._validar_estructura(datos_una_hoja)
        
        assert resultado is False
        assert "debe tener exactamente 2 hojas" in mensaje
        
        # Test con columnas faltantes
        df_sin_columnas = pd.DataFrame({'ColIncorrecta': [1, 2, 3]})
        datos_sin_columnas = {
            'ATC': df_sin_columnas,
            'Encuesta salida': df_sin_columnas
        }
        resultado, mensaje = self.servicio._validar_estructura(datos_sin_columnas)
        
        assert resultado is False
        assert "debe contener la columna" in mensaje
    
    def test_validar_estructura_datos_nulos(self):
        """Test con datos nulos o tipos incorrectos"""
        # Test con DataFrame en lugar de dict
        df = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
        resultado, mensaje = self.servicio._validar_estructura(df)
        
        assert resultado is False
        assert "debe contener exactamente dos hojas" in mensaje
        
        # Test con dict vacío
        resultado, mensaje = self.servicio._validar_estructura({})
        
        assert resultado is False
        assert "debe tener exactamente 2 hojas" in mensaje
        
        # Test con None
        resultado, mensaje = self.servicio._validar_estructura(None)
        
        assert resultado is False
        assert "debe contener exactamente dos hojas" in mensaje
    
    # Tests para obtener_datos_archivo
    def test_obtener_datos_archivo_datos_validos(self, archivo_excel_valido_stream):
        """Test con datos válidos almacenados"""
        # Primero cargar datos válidos
        self.servicio.leer_archivo(archivo_excel_valido_stream, "archivo.xlsx")
        
        resultado = self.servicio.obtener_datos_archivo()
        
        assert resultado is not None
        assert isinstance(resultado, dict)
        assert 'ATC' in resultado
        assert 'Encuesta salida' in resultado
    
    def test_obtener_datos_archivo_sin_datos(self):
        """Test sin datos cargados previamente"""
        resultado = self.servicio.obtener_datos_archivo()
        
        assert resultado is None
    
    def test_obtener_datos_archivo_datos_nulos(self):
        """Test después de intentar cargar datos nulos"""
        # Intentar cargar archivo inválido
        buffer = BytesIO(b"contenido invalido")
        self.servicio.leer_archivo(buffer, "archivo.txt")
        
        resultado = self.servicio.obtener_datos_archivo()
        
        assert resultado is None