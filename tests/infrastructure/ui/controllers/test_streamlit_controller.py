import pytest
import pandas as pd
from unittest.mock import MagicMock, patch, mock_open
from infrastructure.ui.controllers.streamlit_controller import StreamlitController
from infrastructure.ui.constants import ALL_ANALYSES_OPTION


@pytest.fixture
def mock_use_cases():
    return {
        'read_file': MagicMock(),
        'process_file': MagicMock(),
        'load_analysis': MagicMock(),
        'list_analyses': MagicMock(),
        'delete_analysis': MagicMock(),
        'prepare_display': MagicMock(),
        'send_email': MagicMock(),
        'save_report': MagicMock(),
        'list_reports': MagicMock(),
        'clear_history': MagicMock(),
        'delete_report': MagicMock(),
        'update_sentiment': MagicMock(),
        'manage_notes': MagicMock(),
        'get_suggestions': MagicMock(),
    }


@pytest.fixture
def controller(mock_use_cases):
    return StreamlitController(
        read_file_use_case=mock_use_cases['read_file'],
        process_file_use_case=mock_use_cases['process_file'],
        load_analysis_use_case=mock_use_cases['load_analysis'],
        list_analyses_use_case=mock_use_cases['list_analyses'],
        delete_analysis_use_case=mock_use_cases['delete_analysis'],
        prepare_analysis_display_use_case=mock_use_cases['prepare_display'],
        send_results_email_use_case=mock_use_cases['send_email'],
        save_report_use_case=mock_use_cases['save_report'],
        list_reports_use_case=mock_use_cases['list_reports'],
        clear_reports_history_use_case=mock_use_cases['clear_history'],
        delete_report_use_case=mock_use_cases['delete_report'],
        update_sentiment_use_case=mock_use_cases['update_sentiment'],
        manage_notes_use_case=mock_use_cases['manage_notes'],
        get_suggestions_use_case=mock_use_cases['get_suggestions'],
    )


def test_handle_file_upload_success(controller, mock_use_cases):
    mock_file = MagicMock()
    mock_file.type = "text/csv"
    mock_use_cases['read_file'].execute.return_value = pd.DataFrame()
    mock_use_cases['process_file'].execute.return_value = pd.DataFrame({'col': [1]})

    success, df, error = controller.handle_file_upload(mock_file, "test_file")

    assert success is True
    assert df is not None
    assert error is None
    mock_use_cases['read_file'].execute.assert_called_once()
    mock_use_cases['process_file'].execute.assert_called_once()


def test_handle_file_upload_error(controller, mock_use_cases):
    mock_file = MagicMock()
    mock_file.type = "text/csv"
    mock_use_cases['read_file'].execute.side_effect = ValueError("Format error")

    success, df, error = controller.handle_file_upload(mock_file, "test_file")

    assert success is False
    assert df is None
    assert "Format error" in error


def test_handle_load_analysis_single_success(controller, mock_use_cases):
    mock_use_cases['load_analysis'].execute.return_value = pd.DataFrame({'col': [1]})

    success, df, error = controller.handle_load_analysis("analysis_1")

    assert success is True
    assert not df.empty
    assert error is None


def test_handle_load_analysis_empty(controller, mock_use_cases):
    mock_use_cases['load_analysis'].execute.return_value = pd.DataFrame()

    success, df, error = controller.handle_load_analysis("analysis_1")

    assert success is False
    assert df is None
    assert "No se encontraron datos" in error


def test_handle_load_all_analyses_success(controller, mock_use_cases):
    # Setup
    mock_use_cases['list_analyses'].execute.return_value = ["analysis_1", "analysis_2"]
    mock_use_cases['load_analysis'].execute.side_effect = [
        pd.DataFrame({'col': [1]}),  # analysis_1
        pd.DataFrame({'col': [2]}),  # analysis_2
    ]

    success, df, error = controller.handle_load_analysis(ALL_ANALYSES_OPTION)

    assert success is True
    assert len(df) == 2
    assert "analysis_name" in df.columns
    assert set(df["analysis_name"].unique()) == {"analysis_1", "analysis_2"}


def test_handle_load_all_analyses_no_saved(controller, mock_use_cases):
    mock_use_cases['list_analyses'].execute.return_value = []

    success, df, error = controller.handle_load_analysis(ALL_ANALYSES_OPTION)

    assert success is False
    assert "No hay análisis guardados" in error


def test_handle_delete_analysis(controller, mock_use_cases):
    mock_use_cases['delete_analysis'].execute.return_value = (True, "Deleted")

    result = controller.handle_delete_analysis("analysis_1")

    assert result == (True, "Deleted")
    mock_use_cases['delete_analysis'].execute.assert_called_with("analysis_1")


def test_get_report_bytes_success(controller):
    with patch('os.path.exists', return_value=True), \
            patch('builtins.open', mock_open(read_data=b'PDF_CONTENT')):

        success, content = controller.get_report_bytes("/path/to/report.pdf")

        assert success is True
        assert content == b'PDF_CONTENT'


def test_get_report_bytes_not_found(controller):
    with patch('os.path.exists', return_value=False):
        success, content = controller.get_report_bytes("/path/to/report.pdf")
        assert success is False
        assert content is None


def test_handle_update_sentiment_success(controller, mock_use_cases):
    mock_use_cases['update_sentiment'].execute.return_value = (True, "new_id", "Updated")

    success, new_id, msg = controller.handle_update_sentiment("id", pd.DataFrame(), [])

    assert success is True
    assert new_id == "new_id"


def test_handle_update_sentiment_exception(controller, mock_use_cases):
    mock_use_cases['update_sentiment'].execute.side_effect = Exception("Update error")

    success, new_id, msg = controller.handle_update_sentiment("id", pd.DataFrame(), [])

    assert success is False
    assert "Error inesperado al actualizar sentimientos" in msg


def test_notes_delegation(controller, mock_use_cases):
    controller.get_notes("analysis_1")
    mock_use_cases['manage_notes'].get_notes.assert_called_with("analysis_1")

    controller.add_note("analysis_1", "content")
    mock_use_cases['manage_notes'].add_note.assert_called_with("analysis_1", "content")

    controller.delete_note(1)
    mock_use_cases['manage_notes'].delete_note.assert_called_with(1)


def test_suggestions_delegation(controller, mock_use_cases):
    df = pd.DataFrame()
    controller.get_ai_suggestions(df)
    mock_use_cases['get_suggestions'].execute.assert_called_with(df)
