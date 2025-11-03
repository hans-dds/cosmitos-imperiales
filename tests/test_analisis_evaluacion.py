import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from src.main.negocio.ServicioAnalisisEvaluacion import ServicioAnalisisEvaluacion

@pytest.fixture
def servicio_analisis_evaluacion():
    with patch('src.main.negocio.ServicioAnalisisEvaluacion.joblib.load'):
        with patch('src.main.negocio.ServicioAnalisisEvaluacion.ServicioAlmacenamiento') as mock_storage:
            sae = ServicioAnalisisEvaluacion('dummy_path')
            sae.servicio_almacenamiento = mock_storage.return_value
            return sae

def test_guardar_analisis(servicio_analisis_evaluacion):
    df = pd.DataFrame({'a': [1]})
    servicio_analisis_evaluacion.servicio_almacenamiento.guardar_analisis_csv.return_value = (True, "csv_ok")
    servicio_analisis_evaluacion.servicio_almacenamiento.guardar_analisis_mysql.return_value = (True, "mysql_ok")

    success, msg = servicio_analisis_evaluacion.guardar_analisis(df, 'test_file', 'test_table')

    assert success is True
    assert "csv_ok" in msg
    assert "mysql_ok" in msg
    servicio_analisis_evaluacion.servicio_almacenamiento.guardar_analisis_csv.assert_called_once_with(df, 'test_file')
    servicio_analisis_evaluacion.servicio_almacenamiento.guardar_analisis_mysql.assert_called_once_with(df, 'test_table')

def test_listar_analisis_guardados(servicio_analisis_evaluacion):
    servicio_analisis_evaluacion.servicio_almacenamiento.listar_analisis_guardados.return_value = ['t1', 't2']
    
    result = servicio_analisis_evaluacion.listar_analisis_guardados()

    assert result == ['t1', 't2']
    servicio_analisis_evaluacion.servicio_almacenamiento.listar_analisis_guardados.assert_called_once()

def test_cargar_analisis_por_nombre(servicio_analisis_evaluacion):
    df = pd.DataFrame({'b': [2]})
    servicio_analisis_evaluacion.servicio_almacenamiento.cargar_analisis_por_nombre.return_value = df

    result = servicio_analisis_evaluacion.cargar_analisis_por_nombre('test_table')

    assert result.equals(df)
    servicio_analisis_evaluacion.servicio_almacenamiento.cargar_analisis_por_nombre.assert_called_once_with('test_table')

def test_guardar_analisis_failure(servicio_analisis_evaluacion):
    df = pd.DataFrame({'a': [1]})
    servicio_analisis_evaluacion.servicio_almacenamiento.guardar_analisis_csv.return_value = (False, "csv_fail")
    servicio_analisis_evaluacion.servicio_almacenamiento.guardar_analisis_mysql.return_value = (True, "mysql_ok")

    success, msg = servicio_analisis_evaluacion.guardar_analisis(df, 'test_file', 'test_table')

    assert success is False
    assert "csv_fail" in msg
    assert "mysql_ok" in msg

@patch('src.main.negocio.ServicioAnalisisEvaluacion.joblib.load')
def test_init_file_not_found(mock_load):
    mock_load.side_effect = FileNotFoundError
    with patch('src.main.negocio.ServicioAnalisisEvaluacion.ServicioAlmacenamiento'):
        sae = ServicioAnalisisEvaluacion('dummy_path')
        assert sae.modelo is None

@patch('src.main.negocio.ServicioAnalisisEvaluacion.joblib.load')
def test_init_exception(mock_load):
    mock_load.side_effect = Exception("Some error")
    with patch('src.main.negocio.ServicioAnalisisEvaluacion.ServicioAlmacenamiento'):
        sae = ServicioAnalisisEvaluacion('dummy_path')
        assert sae.modelo is None
