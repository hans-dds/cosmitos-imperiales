import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from mysql.connector import Error
from adapters.repositories.analysis_repository_adapter import SQLandCSVAnalysisRepository


@pytest.fixture
def db_config():
    return {
        'host': 'localhost',
        'user': 'user',
        'password': 'password',
        'database': 'test_db'
    }


@pytest.fixture
def repo(db_config):
    # We patch makedirs in the fixture/init to avoid side effects during setup
    with patch('os.makedirs'):
        return SQLandCSVAnalysisRepository(db_config, csv_base_dir="test_csv_dir")


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'comentarios': ['Test comment'],
        'calificacion': [5.0],
        'Clasificacion': ['Positive'],
        'Fiabilidad': ['High'],
        'fecha': ['2023-01-01']
    })


def test_init_creates_dir(db_config):
    with patch('os.makedirs') as mock_makedirs:
        SQLandCSVAnalysisRepository(db_config, "new_dir")
        mock_makedirs.assert_called_with("new_dir", exist_ok=True)


@patch('adapters.repositories.analysis_repository_adapter.os.path.join')
@patch('pandas.DataFrame.to_csv')
def test_save_csv_success(mock_to_csv, mock_join, repo, sample_data):
    mock_join.return_value = "test_csv_dir/test_id_limpio.csv"

    success, msg = repo._save_csv(sample_data, "test_id")

    assert success is True
    assert "Datos guardados exitosamente" in msg
    mock_to_csv.assert_called_once()


def test_save_csv_empty_data(repo):
    success, msg = repo._save_csv(pd.DataFrame(), "test_id")
    assert success is False
    assert msg == "No se proporcionaron datos para guardar."


@patch('pandas.DataFrame.to_csv')
def test_save_csv_exception(mock_to_csv, repo, sample_data):
    mock_to_csv.side_effect = Exception("Disk full")
    success, msg = repo._save_csv(sample_data, "test_id")
    assert success is False
    assert "Fallo al guardar el archivo CSV" in msg


@patch('mysql.connector.connect')
def test_save_mysql_success(mock_connect, repo, sample_data):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    # Mock context manager: with connect() as conn
    mock_connect.return_value.__enter__.return_value = mock_conn
    # Mock context manager: with conn.cursor() as cursor
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    success, msg = repo._save_mysql(sample_data, "analisis_test")

    assert success is True
    assert "Datos guardados exitosamente en la tabla MySQL" in msg
    mock_cursor.execute.assert_called()
    mock_conn.commit.assert_called_once()


@patch('mysql.connector.connect')
def test_save_mysql_invalid_table_name(mock_connect, repo, sample_data):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    success, msg = repo._save_mysql(sample_data, "analisis;DROP TABLE")

    assert success is False
    assert "Nombre de tabla inválido" in msg
    mock_cursor.execute.assert_not_called()


@patch('mysql.connector.connect')
def test_save_mysql_connection_error(mock_connect, repo, sample_data):
    mock_connect.side_effect = Error("Connection failed")
    success, msg = repo._save_mysql(sample_data, "analisis_test")
    assert success is False
    assert "Error al conectar o guardar en MySQL" in msg


@patch('adapters.repositories.analysis_repository_adapter.SQLandCSVAnalysisRepository._save_mysql')
@patch('adapters.repositories.analysis_repository_adapter.SQLandCSVAnalysisRepository._save_csv')
def test_save_main_method(mock_save_csv, mock_save_mysql, repo, sample_data):
    # Case 1: Both success
    mock_save_csv.return_value = (True, "CSV Ok")
    mock_save_mysql.return_value = (True, "SQL Ok")

    success, msg = repo.save(sample_data, "test_id")
    assert success is True
    assert msg == "Persistencia realizada en CSV y MySQL."

    # Case 2: CSV Success, SQL Fail
    mock_save_mysql.return_value = (False, "SQL Fail")
    success, msg = repo.save(sample_data, "test_id")
    assert success is False
    assert "CSV OK. MySQL fallo" in msg

    # Case 3: SQL Success, CSV Fail
    mock_save_mysql.return_value = (True, "SQL Ok")
    mock_save_csv.return_value = (False, "CSV Fail")
    success, msg = repo.save(sample_data, "test_id")
    assert success is False
    assert "MySQL OK. CSV fallo" in msg


@patch('mysql.connector.connect')
def test_list_success(mock_connect, repo):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [('analisis_1',), ('analisis_2',)]

    tables = repo.list()
    assert tables == ['analisis_1', 'analisis_2']


@patch('mysql.connector.connect')
def test_list_error(mock_connect, repo):
    mock_connect.side_effect = Error("DB Error")
    tables = repo.list()
    assert tables == []


@patch('pandas.read_sql')
@patch('mysql.connector.connect')
def test_load_success(mock_connect, mock_read_sql, repo):
    mock_conn = MagicMock()
    mock_connect.return_value.__enter__.return_value = mock_conn

    expected_df = pd.DataFrame({'col': [1, 2]})
    mock_read_sql.return_value = expected_df

    df = repo.load("analisis_1")
    pd.testing.assert_frame_equal(df, expected_df)
    mock_read_sql.assert_called_once()


@patch('mysql.connector.connect')
def test_load_invalid_id(mock_connect, repo):
    df = repo.load("invalid id;")
    assert df.empty


@patch('mysql.connector.connect')
def test_delete_success(mock_connect, repo):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    # Mock table exists
    mock_cursor.fetchone.return_value = ('analisis_test',)

    with patch('os.path.exists') as mock_exists, patch('os.remove') as mock_remove:
        mock_exists.return_value = True

        success, msg = repo.delete("analisis_test")

        assert success is True
        mock_cursor.execute.assert_any_call("DROP TABLE IF EXISTS `analisis_test`")
        mock_remove.assert_called_once()


@patch('mysql.connector.connect')
def test_delete_not_found(mock_connect, repo):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    # Mock table DOES NOT exist
    mock_cursor.fetchone.return_value = None

    success, msg = repo.delete("analisis_unknown")

    assert success is False
    assert "no existe en la base de datos" in msg


@patch('adapters.repositories.analysis_repository_adapter.SQLandCSVAnalysisRepository.save')
@patch('mysql.connector.connect')
def test_clone_with_modifications_success(mock_connect, mock_save, repo, sample_data):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    # Mock original exists
    mock_cursor.fetchone.return_value = ('analisis_orig',)

    # Mock save success
    mock_save.return_value = (True, "Saved")

    success, new_id, msg = repo.clone_with_modifications(
        "analisis_orig", sample_data, "_v2"
    )

    assert success is True
    assert new_id == "analisis_orig_v2"
