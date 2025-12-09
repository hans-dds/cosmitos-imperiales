import pytest
from unittest.mock import MagicMock, patch, call
from adapters.repositories.report_repository_adapter import SQLReportRepository

@pytest.fixture
def db_config():
    return {'host': 'localhost', 'user': 'test', 'password': 'pwd', 'database': 'db'}

@pytest.fixture
def mock_mysql():
    with patch('adapters.repositories.report_repository_adapter.mysql.connector') as mock:
        yield mock

@pytest.fixture
def mock_os():
    with patch('adapters.repositories.report_repository_adapter.os') as mock:
        yield mock

def test_ensure_table_exists(db_config, mock_mysql, mock_os):
    repo = SQLReportRepository(db_config, 'reports_dir')
    
    mock_mysql.connect.assert_called_with(**db_config)
    cursor = mock_mysql.connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
    assert cursor.execute.call_count >= 1
    # Check if table creation SQL was sent
    assert "CREATE TABLE IF NOT EXISTS report_history" in cursor.execute.call_args[0][0]

def test_fetch_all_paths(db_config, mock_mysql, mock_os):
    mock_os.makedirs.return_value = None
    repo = SQLReportRepository(db_config)
    
    cursor = mock_mysql.connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
    cursor.fetchall.return_value = [('path/to/file1',), ('path/to/file2',)]
    
    paths = repo._fetch_all_paths()
    assert paths == ['path/to/file1', 'path/to/file2']

def test_delete_files(db_config, mock_mysql, mock_os):
    repo = SQLReportRepository(db_config)
    paths = ['file1', 'file2']
    def side_effect(arg):
        return arg == 'file1'
    mock_os.path.exists.side_effect = side_effect
    
    deleted = repo._delete_files(paths)
    
    assert deleted == 1
    mock_os.remove.assert_called_once_with('file1')

def test_save_success(db_config, mock_mysql, mock_os):
    repo = SQLReportRepository(db_config)
    
    success, msg = repo.save(
        analysis_name='test',
        report_format='pdf',
        file_path='/tmp/file.pdf'
    )
    
    assert success is True
    assert "guardado" in msg
    cursor = mock_mysql.connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
    assert "INSERT INTO report_history" in cursor.execute.call_args[0][0]

def test_list_reports(db_config, mock_mysql, mock_os):
    repo = SQLReportRepository(db_config)
    
    cursor = mock_mysql.connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
    expected_rows = [{'id': 1, 'analysis_name': 'test'}]
    cursor.fetchall.return_value = expected_rows
    
    rows = repo.list()
    assert rows == expected_rows

def test_get_report(db_config, mock_mysql, mock_os):
    repo = SQLReportRepository(db_config)
    
    cursor = mock_mysql.connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
    expected_row = {'id': 1, 'analysis_name': 'test'}
    cursor.fetchone.return_value = expected_row
    
    row = repo.get(1)
    assert row == expected_row

def test_delete_report_success(db_config, mock_mysql, mock_os):
    repo = SQLReportRepository(db_config)
    
    con = mock_mysql.connect.return_value.__enter__.return_value
    cursor = con.cursor.return_value.__enter__.return_value
    
    # Mock finding the file path
    cursor.fetchone.return_value = {'file_path': '/tmp/file.pdf'}
    mock_os.path.exists.return_value = True
    
    success, msg = repo.delete(1)
    
    assert success is True
    mock_os.remove.assert_called_with('/tmp/file.pdf')
    # Verify DB deletion call
    assert "DELETE FROM report_history" in cursor.execute.call_args_list[-1][0][0]

def test_clear_history(db_config, mock_mysql, mock_os):
    repo = SQLReportRepository(db_config)
    
    # Mock fetching paths
    # We need to mock _fetch_all_paths logic by manipulating the cursor responses
    # First connect/cursor context is ensuring table (init)
    # Second connect/cursor context: _fetch_all_paths inside clear()
    # Third connect/cursor context: TRUNCATE inside clear()
    
    # It's easier to mock the methods if we wanted, but let's stick to mocking DB layers
    con_mock = mock_mysql.connect.return_value.__enter__.return_value
    cursor_mock = con_mock.cursor.return_value.__enter__.return_value
    
    # Setup fetchall for _fetch_all_paths (called first inside clear)
    cursor_mock.fetchall.side_effect = [
        [('/tmp/file1',), ('/tmp/file2',)], # For _fetch_all_paths
        [] 
    ]
    mock_os.path.exists.return_value = True
    
    success, msg = repo.clear()
    
    assert success is True
    assert mock_os.remove.call_count == 2
    assert "TRUNCATE TABLE report_history" in cursor_mock.execute.call_args_list[-1][0][0]
