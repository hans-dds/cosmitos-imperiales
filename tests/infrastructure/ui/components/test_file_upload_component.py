import pytest
from unittest.mock import MagicMock, patch
from infrastructure.ui.components.file_upload_component import FileUploadComponent

class MockSessionState:
    def __init__(self):
        self._state = {}
    
    def __getattr__(self, name):
        if name in self._state:
            return self._state[name]
        raise AttributeError(f"st.session_state has no attribute '{name}'")
        
    def __setattr__(self, name, value):
        if name == "_state":
            super().__setattr__(name, value)
        else:
            self._state[name] = value
            
    def __contains__(self, key):
        return key in self._state
    
    def get(self, key, default=None):
        return self._state.get(key, default)

@pytest.fixture
def mock_streamlit():
    with patch('infrastructure.ui.components.file_upload_component.st') as mock:
        # Replace session_state with our custom class that supports attribute access
        mock.session_state = MockSessionState()
        yield mock

def test_render_no_file(mock_streamlit):
    comp = FileUploadComponent()
    mock_streamlit.sidebar.file_uploader.return_value = None
    
    result = comp.render()
    
    assert result is None
    mock_streamlit.sidebar.header.assert_called_with("📁 Cargar y Analizar Archivo")

def test_render_new_file_clears_selection(mock_streamlit):
    comp = FileUploadComponent()
    
    # Mock uploaded file
    uploaded_file = MagicMock()
    uploaded_file.name = "data.csv"
    uploaded_file.size = 100
    mock_streamlit.sidebar.file_uploader.return_value = uploaded_file
    
    # Pre-set session state to simulate a selected analysis
    mock_streamlit.session_state.selected_analysis = "Old Analysis"
    # Ensure 'last_processed_file' is NOT set, so it looks like a new file
    
    result = comp.render()
    
    assert result == uploaded_file
    # Should have cleared selected_analysis because it's a new file (not matched in state)
    assert mock_streamlit.session_state.selected_analysis is None

def test_render_same_file_keeps_selection(mock_streamlit):
    comp = FileUploadComponent()
    
    uploaded_file = MagicMock()
    uploaded_file.name = "data.csv"
    uploaded_file.size = 100
    file_id = "data.csv_100"
    mock_streamlit.sidebar.file_uploader.return_value = uploaded_file
    
    # Set state as if this file was already processed
    mock_streamlit.session_state.last_processed_file = file_id
    mock_streamlit.session_state.selected_analysis = "Current Analysis"
    
    result = comp.render()
    
    assert result == uploaded_file
    # Should NOT clear selection
    assert mock_streamlit.session_state.selected_analysis == "Current Analysis"
