import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from unittest.mock import patch, MagicMock
from main.negocio.ServicioLimpiarDatos import ServicioLimpiarDatos

class TestServicioLimpiarDatos:
    
    def setup_method(self):
        """Setup para cada test"""
        self.servicio = ServicioLimpiarDatos()
    
    @pytest.fixture
    def df_valido(self):
        """DataFrame con datos válidos"""
        return pd.DataFrame({
            'Calificacion': [5, 4, 3, 2, 1],
            'Comentarios': ['Excelente servicio', 'Muy bueno', 'Regular atención', 'Malo el trato', 'Pésimo servicio']
        })
    
    @pytest.fixture
    def df_invalido(self):
        """DataFrame con datos inválidos"""
        return pd.DataFrame({
            'Calificacion': ['abc', '5 puntos', '', None, 'texto'],
            'Comentarios': ['', 'solo califica', 'na', None, '   ']
        })
    
    @pytest.fixture
    def df_nulo(self):
        """DataFrame vacío o con valores nulos"""
        return pd.DataFrame({
            'Calificacion': [None, None, None],
            'Comentarios': [None, None, None]
        })
    
    @pytest.fixture
    def archivo_excel_valido(self, df_valido):
        """Archivo Excel temporal con datos válidos"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            with pd.ExcelWriter(tmp.name, engine='openpyxl') as writer:
                df_valido.to_excel(writer, sheet_name='ATC', index=False)
                df_valido.to_excel(writer, sheet_name='Encuesta salida', index=False)
            yield tmp.name
        os.unlink(tmp.name)
    
    # Tests para _leer_y_unificar_excel
    def test_leer_y_unificar_excel_datos_validos(self, archivo_excel_valido):
        """Test con archivo Excel válido"""
        resultado = self.servicio._leer_y_unificar_excel(archivo_excel_valido)
        
        assert not resultado.empty
        assert 'calificacion' in resultado.columns
        assert 'comentarios' in resultado.columns
        assert len(resultado) == 10  # 5 filas de cada hoja
    
    def test_leer_y_unificar_excel_datos_invalidos(self):
        """Test con archivo inexistente o inválido"""
        resultado = self.servicio._leer_y_unificar_excel('archivo_inexistente.xlsx')
        
        assert resultado.empty
    
    def test_leer_y_unificar_excel_datos_nulos(self):
        """Test con ruta nula"""
        resultado = self.servicio._leer_y_unificar_excel('')
        
        assert resultado.empty
    
    # Tests para _limpiar_calificaciones
    def test_limpiar_calificaciones_datos_validos(self):
        """Test con calificaciones válidas"""
        df = pd.DataFrame({
            'calificacion': [5, 4, 3, 2, 1],
            'comentarios': ['test1', 'test2', 'test3', 'test4', 'test5']
        })
        
        resultado = self.servicio._limpiar_calificaciones(df)
        
        assert len(resultado) == 5
        assert resultado['calificacion'].dtype == 'Int8'
        assert all(resultado['calificacion'].between(1, 5))
    
    def test_limpiar_calificaciones_datos_invalidos(self):
        """Test con calificaciones inválidas"""
        df = pd.DataFrame({
            'calificacion': ['abc', '5 puntos', 'texto', '10.5', ''],
            'comentarios': ['test1', 'test2', 'test3', 'test4', 'test5']
        })
        
        resultado = self.servicio._limpiar_calificaciones(df)
        
        # Solo '5 puntos' debería convertirse a 5 (los decimales se eliminan)
        assert len(resultado) == 1
        assert resultado.iloc[0]['calificacion'] == 5
    
    def test_limpiar_calificaciones_datos_nulos(self):
        """Test con calificaciones nulas"""
        df = pd.DataFrame({
            'calificacion': [None, np.nan, '', None],
            'comentarios': ['test1', 'test2', 'test3', 'test4']
        })
        
        resultado = self.servicio._limpiar_calificaciones(df)
        
        assert resultado.empty
    
    # Tests para _limpiar_texto_individual
    def test_limpiar_texto_individual_datos_validos(self):
        """Test con texto válido"""
        texto = "¡Excelente Servicio! Me gustó mucho."
        
        resultado = self.servicio._limpiar_texto_individual(texto)
        
        assert resultado == "excelente servicio me gusto mucho"
        assert isinstance(resultado, str)
    
    def test_limpiar_texto_individual_datos_invalidos(self):
        """Test con texto inválido (solo espacios y puntuación)"""
        texto = "   !!!   ??? ... "
        
        resultado = self.servicio._limpiar_texto_individual(texto)
        
        assert pd.isna(resultado)
    
    def test_limpiar_texto_individual_datos_nulos(self):
        """Test con datos nulos"""
        textos_nulos = [None, '', '   ', np.nan, 123]
        
        for texto in textos_nulos:
            resultado = self.servicio._limpiar_texto_individual(texto)
            assert pd.isna(resultado)
    
    # Tests para _filtrar_comentarios_irrelevantes
    def test_filtrar_comentarios_irrelevantes_datos_validos(self):
        """Test con comentarios válidos"""
        df = pd.DataFrame({
            'calificacion': [5, 4, 3],
            'comentarios': ['excelente atencion al cliente', 'muy buen servicio rapido', 'atencion regular pero mejorable']
        })
        
        resultado = self.servicio._filtrar_comentarios_irrelevantes(df)
        
        assert len(resultado) == 3
        assert all(resultado['comentarios'].str.len() >= 5)
    
    def test_filtrar_comentarios_irrelevantes_datos_invalidos(self):
        """Test con comentarios irrelevantes"""
        df = pd.DataFrame({
            'calificacion': [5, 4, 3, 2, 1],
            'comentarios': ['solo califica', 'sin comentarios', 'ninguno', 'ok', 'na']
        })
        
        resultado = self.servicio._filtrar_comentarios_irrelevantes(df)
        
        assert resultado.empty
    
    def test_filtrar_comentarios_irrelevantes_datos_nulos(self):
        """Test con comentarios nulos"""
        df = pd.DataFrame({
            'calificacion': [5, 4, 3],
            'comentarios': [None, np.nan, '']
        })
        
        resultado = self.servicio._filtrar_comentarios_irrelevantes(df)
        
        assert resultado.empty
    
    # Tests para procesar_archivo_excel
    @patch('main.negocio.ServicioLimpiarDatos.GuardarDatosArchivo')
    def test_procesar_archivo_excel_datos_validos(self, mock_guardar, archivo_excel_valido):
        """Test con archivo Excel válido"""
        mock_instance = MagicMock()
        mock_guardar.return_value = mock_instance
        
        resultado = self.servicio.procesar_archivo_excel(archivo_excel_valido)
        
        mock_instance.guardar_datos_limpios.assert_called_once()
        assert resultado is None  # La función retorna None
    
    @patch('main.negocio.ServicioLimpiarDatos.GuardarDatosArchivo')
    def test_procesar_archivo_excel_datos_invalidos(self, mock_guardar):
        """Test con archivo inexistente"""
        mock_instance = MagicMock()
        mock_guardar.return_value = mock_instance
        
        resultado = self.servicio.procesar_archivo_excel('archivo_inexistente.xlsx')
        
        mock_instance.guardar_datos_limpios.assert_not_called()
        assert resultado is None
    
    @patch('main.negocio.ServicioLimpiarDatos.GuardarDatosArchivo')
    def test_procesar_archivo_excel_datos_nulos(self, mock_guardar):
        """Test con ruta nula"""
        mock_instance = MagicMock()
        mock_guardar.return_value = mock_instance
        
        resultado = self.servicio.procesar_archivo_excel('')
        
        mock_instance.guardar_datos_limpios.assert_not_called()
        assert resultado is None
    
    # Tests para procesar_datos_en_memoria
    def test_procesar_datos_en_memoria_datos_validos(self, df_valido):
        """Test con datos válidos en memoria"""
        datos = {
            'ATC': df_valido,
            'Encuesta salida': df_valido
        }
        
        resultado = self.servicio.procesar_datos_en_memoria(datos)
        
        assert not resultado.empty
        assert 'calificacion' in resultado.columns
        assert 'comentarios' in resultado.columns
        assert len(resultado) > 0
    
    def test_procesar_datos_en_memoria_datos_invalidos(self):
        """Test con datos inválidos (hojas incorrectas)"""
        datos = {
            'HojaIncorrecta': pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
        }
        
        resultado = self.servicio.procesar_datos_en_memoria(datos)
        
        assert resultado.empty
    
    def test_procesar_datos_en_memoria_datos_nulos(self):
        """Test con datos nulos o vacíos"""
        datos_nulos = [None, {}, {'ATC': pd.DataFrame()}, {'Encuesta salida': None}]
        
        for datos in datos_nulos:
            if datos is None:
                with pytest.raises(TypeError):
                    self.servicio.procesar_datos_en_memoria(datos)
            else:
                resultado = self.servicio.procesar_datos_en_memoria(datos)
                assert resultado.empty