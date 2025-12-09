import pytest
from unittest.mock import MagicMock, patch
from infrastructure.ui.components.report_history_component import ReportHistoryComponent

@pytest.fixture
def mock_controller():
    return MagicMock()

@pytest.fixture
def mock_streamlit():
    with patch('infrastructure.ui.components.report_history_component.st') as mock:
        mock.button.return_value = False
        yield mock

def test_render_empty_history(mock_controller, mock_streamlit):
    comp = ReportHistoryComponent()
    mock_controller.get_report_history.return_value = []
    
    comp.render(mock_controller)
    
    mock_streamlit.info.assert_called_with("No hay reportes guardados aún.")

def test_render_populated_history_download_success(mock_controller, mock_streamlit):
    comp = ReportHistoryComponent()
    mock_controller.get_report_history.return_value = [
        {
            "id": "1",
            "source_file_name": "test.pdf",
            "report_format": "pdf",
            "created_at": "2023-01-01",
            "file_path": "/path/to/test.pdf"
        }
    ]
    
    # Mock columns
    cols = [MagicMock() for _ in range(5)]
    mock_streamlit.columns.return_value = cols
    
    # Mock file bytes
    mock_controller.get_report_bytes.return_value = (True, b"pdf_content")
    
    comp.render(mock_controller)
    
    mock_streamlit.columns.assert_called()
    mock_streamlit.download_button.assert_called()
    # verify mime type for pdf
    args, kwargs = mock_streamlit.download_button.call_args
    assert kwargs['mime'] == "application/pdf"

def test_render_file_missing(mock_controller, mock_streamlit):
    comp = ReportHistoryComponent()
    mock_controller.get_report_history.return_value = [
        {
            "id": "1",
            "source_file_name": "test.xlsx",
            "report_format": "excel",
            "created_at": "2023-01-01",
            "file_path": "/path/to/test.xlsx"
        }
    ]
    
    # Mock columns
    cols = [MagicMock() for _ in range(5)]
    mock_streamlit.columns.return_value = cols
    
    # File missing
    mock_controller.get_report_bytes.return_value = (False, None)
    
    comp.render(mock_controller)
    
    mock_streamlit.button.assert_any_call("Archivo no disponible", disabled=True, key="missing_1")

def test_delete_report_success(mock_controller, mock_streamlit):
    comp = ReportHistoryComponent()
    mock_controller.get_report_history.return_value = [
        {"id": "1", "source_file_name": "test", "report_format": "pdf", "created_at": "date", "file_path": "path"}
    ]
    
    cols = [MagicMock() for _ in range(5)]
    mock_streamlit.columns.return_value = cols
    
    # Simulate delete click
    def button_side_effect(*args, **kwargs):
        # The delete button is in cols[4], but we can just check keys broadly or assume st.button calls
        if kwargs.get('key') == "del_1":
            return True
        return False
    mock_streamlit.button.side_effect = button_side_effect
    
    mock_controller.delete_report.return_value = (True, "Deleted")
    mock_controller.get_report_bytes.return_value = (True, b"data")
    
    comp.render(mock_controller)
    
    mock_controller.delete_report.assert_called_with("1")
    mock_streamlit.toast.assert_called_with("Deleted")
    mock_streamlit.rerun.assert_called()

def test_clear_history_success(mock_controller, mock_streamlit):
    comp = ReportHistoryComponent()
    # Mock expander interactions logic is implicit in with block
    
    # Simulate clear button click
    # The clear button is inside render_actions
    # We need to simulate that specific button returning True
    def button_side_effect(*args, **kwargs):
        if kwargs.get('type') == 'primary' and 'Limpiar' in args[0]:
            return True
        return False
    mock_streamlit.button.side_effect = button_side_effect
    
    mock_controller.clear_report_history.return_value = (True, "Cleared")
    mock_controller.get_report_history.return_value = []
    
    comp.render(mock_controller)
    
    mock_controller.clear_report_history.assert_called()
    mock_streamlit.success.assert_called_with("Cleared")
