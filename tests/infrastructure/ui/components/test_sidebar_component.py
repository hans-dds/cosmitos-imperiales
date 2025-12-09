import pytest
from unittest.mock import MagicMock, patch
from infrastructure.ui.components.sidebar_component import SidebarComponent

@pytest.fixture
def mock_controller():
    return MagicMock()

class MockSessionState(dict):
    """Mock for streamlit session state that supports attribute access"""
    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError(f"MockSessionState has no attribute {item}")
    
    def __setattr__(self, key, value):
        self[key] = value

@pytest.fixture
def mock_streamlit():
    with patch('infrastructure.ui.components.sidebar_component.st') as mock:
        mock.session_state = MockSessionState()
        yield mock

@pytest.fixture
def mock_components():
    with patch('infrastructure.ui.components.sidebar_component.FileUploadComponent') as file_upload, \
         patch('infrastructure.ui.components.sidebar_component.DeleteAnalysisComponent') as delete_analysis, \
         patch('infrastructure.ui.constants.ALL_ANALYSES_OPTION', "Todas"):
         
        file_upload.return_value.render.return_value = None
        
        yield {
            'file_upload': file_upload.return_value,
            'delete_analysis': delete_analysis.return_value
        }

def test_render_uploaded_file(mock_controller, mock_streamlit, mock_components):
    comp = SidebarComponent(mock_controller)
    mock_file = MagicMock()
    mock_components['file_upload'].render.return_value = mock_file
    
    mock_controller.get_saved_analyses.return_value = []
    
    uploaded, loaded = comp.render()
    
    assert uploaded == mock_file
    assert loaded is None

def test_render_saved_analyses_selection(mock_controller, mock_streamlit, mock_components):
    comp = SidebarComponent(mock_controller)
    
    saved_analyses = ["analisis_1", "analisis_2"]
    mock_controller.get_saved_analyses.return_value = saved_analyses
    
    # Simulate selecting "analisis_1"
    mock_streamlit.sidebar.selectbox.return_value = "analisis_1"
    
    uploaded, loaded = comp.render()
    
    assert loaded == "analisis_1"
    # Verify delete component render call
    mock_components['delete_analysis'].render.assert_called_with(saved_analyses, embedded=False)

def test_render_no_saved_analyses(mock_controller, mock_streamlit, mock_components):
    comp = SidebarComponent(mock_controller)
    
    mock_controller.get_saved_analyses.return_value = []
    
    comp.render()
    
    mock_streamlit.sidebar.info.assert_called_with("No hay análisis guardados en la base de datos.")
    assert mock_streamlit.session_state["selected_analysis"] is None

def test_automatic_selection_update(mock_controller, mock_streamlit, mock_components):
    comp = SidebarComponent(mock_controller)
    
    mock_controller.get_saved_analyses.return_value = ["analisis_1"]
    
    # Current state is different
    mock_streamlit.session_state.selected_analysis = "old_selection"
    
    # New selection from UI
    mock_streamlit.sidebar.selectbox.return_value = "analisis_1"
    
    uploaded, loaded = comp.render()
    
    # Should update session state
    assert mock_streamlit.session_state["selected_analysis"] == "analisis_1"
    assert loaded == "analisis_1"
