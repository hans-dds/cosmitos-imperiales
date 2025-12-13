import pytest
from unittest.mock import patch
from adapters.repositories.note_repository_adapter import SQLNoteRepository


@pytest.fixture
def db_config():
    return {'host': 'localhost', 'user': 'test', 'password': 'pwd', 'database': 'db'}


@pytest.fixture
def mock_mysql():
    with patch('adapters.repositories.note_repository_adapter.mysql.connector') as mock:
        yield mock


def test_add_note_success(db_config, mock_mysql):
    repo = SQLNoteRepository(db_config)

    success, msg = repo.add('analysis_1', 'my note content')

    assert success is True
    assert "guardada" in msg

    con = mock_mysql.connect.return_value.__enter__.return_value
    cursor = con.cursor.return_value.__enter__.return_value

    # Check ensure table exists calls
    assert "CREATE TABLE IF NOT EXISTS `report_notes`" in (
        cursor.execute.call_args_list[0][0][0]
    )
    # Check insert
    assert "INSERT INTO report_notes" in cursor.execute.call_args_list[1][0][0]
    assert ('analysis_1', 'my note content') == cursor.execute.call_args_list[1][0][1]


def test_add_note_failure(db_config, mock_mysql):
    # Patch the Error class imported in the module so it catches our raised exception
    with patch('adapters.repositories.note_repository_adapter.Error', Exception):
        repo = SQLNoteRepository(db_config)

        # Simulate DB error on connect
        mock_mysql.connect.side_effect = Exception("Connection fails")

        success, msg = repo.add('a', 'b')
        assert success is False
        assert "Error BD" in msg


def test_get_all_notes(db_config, mock_mysql):
    repo = SQLNoteRepository(db_config)

    cursor = (
        mock_mysql.connect.return_value.__enter__.return_value
        .cursor.return_value.__enter__.return_value
    )
    expected_rows = [{'id': 1, 'note_content': 'abc'}]
    cursor.fetchall.return_value = expected_rows

    notes = repo.get_all('analysis_1')

    assert notes == expected_rows
    # Check filtering by analysis name
    assert "WHERE analysis_name = %s" in cursor.execute.call_args[0][0]


def test_delete_note_success(db_config, mock_mysql):
    repo = SQLNoteRepository(db_config)

    success, msg = repo.delete(123)

    assert success is True
    cursor = (
        mock_mysql.connect.return_value.__enter__.return_value
        .cursor.return_value.__enter__.return_value
    )
    assert "DELETE FROM report_notes" in cursor.execute.call_args[0][0]
    assert (123,) == cursor.execute.call_args[0][1]
