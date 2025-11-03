import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from src.main.negocio.ServicioAlmacenamiento import ServicioAlmacenamiento
from src.main.datos.GuardarDatosArchivo import GuardarDatosArchivo
from mysql.connector import Error

@pytest.fixture
def db_config():
    return {
        'host': 'localhost',
        'user': 'test_user',
        'password': 'test_password',
        'database': 'test_db'
    }

@pytest.fixture
def servicio_almacenamiento(db_config):
    return ServicioAlmacenamiento(db_config)

@pytest.fixture
def sample_dataframe():
    data = {
        'comentarios': ['bueno', 'malo'],
        'calificacion': [5.0, 1.0],
        'Clasificacion': ['Positivo', 'Negativo']
    }
    return pd.DataFrame(data)

def test_guardar_analisis_csv(servicio_almacenamiento, sample_dataframe):
    with patch.object(servicio_almacenamiento.guardar_datos_csv, 'guardar_datos_limpios', return_value=(True, "Success")) as mock_guardar:
        success, msg = servicio_almacenamiento.guardar_analisis_csv(sample_dataframe, 'test_file')
        assert success is True
        assert msg == "Success"
        mock_guardar.assert_called_once_with(sample_dataframe, 'test_file')

@patch('src.main.negocio.ServicioAlmacenamiento.mysql.connector.connect')
def test_guardar_analisis_mysql_success(mock_connect, servicio_almacenamiento, sample_dataframe):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    success, msg = servicio_almacenamiento.guardar_analisis_mysql(sample_dataframe, 'test_table')

    assert success is True
    assert "exitosamente" in msg
    mock_connect.assert_called_once()
    assert mock_cursor.execute.call_count == 3 # 1 for CREATE TABLE, 2 for INSERT
    mock_conn.commit.assert_called_once()

@patch('src.main.negocio.ServicioAlmacenamiento.mysql.connector.connect')
def test_listar_analisis_guardados_success(mock_connect, servicio_almacenamiento):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [('analisis_1',), ('analisis_2',)]

    tables = servicio_almacenamiento.listar_analisis_guardados()

    assert tables == ['analisis_1', 'analisis_2']
    mock_cursor.execute.assert_called_once_with("SHOW TABLES LIKE 'analisis_%'")

@patch('src.main.negocio.ServicioAlmacenamiento.pd.read_sql')
@patch('src.main.negocio.ServicioAlmacenamiento.mysql.connector.connect')
def test_cargar_analisis_por_nombre_success(mock_connect, mock_read_sql, servicio_almacenamiento, sample_dataframe):
    mock_connect.return_value = MagicMock()
    mock_read_sql.return_value = sample_dataframe

    df = servicio_almacenamiento.cargar_analisis_por_nombre('test_table')

    assert not df.empty
    assert df.equals(sample_dataframe)
    mock_read_sql.assert_called_once()

@patch('src.main.negocio.ServicioAlmacenamiento.mysql.connector.connect')
def test_guardar_analisis_mysql_failure(mock_connect, servicio_almacenamiento, sample_dataframe):
    mock_connect.side_effect = Error("DB error")
    success, msg = servicio_almacenamiento.guardar_analisis_mysql(sample_dataframe, 'test_table')
    assert success is False
    assert "DB error" in msg

@patch('src.main.negocio.ServicioAlmacenamiento.mysql.connector.connect')
def test_listar_analisis_guardados_failure(mock_connect, servicio_almacenamiento):
    mock_connect.side_effect = Error("DB error")
    tables = servicio_almacenamiento.listar_analisis_guardados()
    assert tables == []

@patch('src.main.negocio.ServicioAlmacenamiento.mysql.connector.connect')
def test_cargar_analisis_por_nombre_failure(mock_connect, servicio_almacenamiento):
    mock_connect.side_effect = Error("DB error")
    df = servicio_almacenamiento.cargar_analisis_por_nombre('test_table')
    assert df.empty
