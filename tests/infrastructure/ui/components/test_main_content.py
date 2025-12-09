import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from infrastructure.ui.components.main_content import MainContent

@pytest.fixture
def mock_controller():
    return MagicMock()

@pytest.fixture
def mock_state_manager():
    with patch('infrastructure.ui.components.main_content.AnalysisStateManager') as mock:
        yield mock.return_value

@pytest.fixture
def mock_components():
    with patch('infrastructure.ui.components.main_content.ChartsComponent') as charts, \
         patch('infrastructure.ui.components.main_content.TableComponent') as table, \
         patch('infrastructure.ui.components.main_content.ExportComponent') as export, \
         patch('infrastructure.ui.components.main_content.WordCloudComponent') as wc, \
         patch('infrastructure.ui.components.main_content.NotesComponent') as notes, \
         patch('infrastructure.ui.components.main_content.AISuggestionsComponent') as ai:
        yield {
            'charts': charts.return_value,
            'table': table.return_value,
            'export': export.return_value,
            'wc': wc.return_value,
            'notes': notes.return_value,
            'ai': ai.return_value
        }

@pytest.fixture
def mock_streamlit():
    with patch('infrastructure.ui.components.main_content.st') as mock:
        mock.session_state = {}
        yield mock

def test_handle_file_upload_success(mock_controller, mock_state_manager, mock_streamlit):
    mc = MainContent(mock_controller)
    file = MagicMock()
    file.name = "test.xlsx"
    file.size = 123
    
    mock_state_manager.is_file_already_processed.return_value = False
    mock_controller.handle_file_upload.return_value = (True, "DF_MOCK", None)
    
    mc._handle_file_upload(file)
    
    # Should call controller
    mock_controller.handle_file_upload.assert_called_with(file, "test")
    # Should update state
    mock_state_manager.set_new_analysis.assert_called()
    # Should rerun
    mock_streamlit.rerun.assert_called()

def test_handle_file_upload_failure(mock_controller, mock_state_manager, mock_streamlit):
    mc = MainContent(mock_controller)
    file = MagicMock()
    file.name = "test.xlsx"
    file.size = 123
    
    mock_state_manager.is_file_already_processed.return_value = False
    mock_controller.handle_file_upload.return_value = (False, None, "Error")
    
    mc._handle_file_upload(file)
    
    mock_streamlit.error.assert_called()
    mock_state_manager.clear_processed_file_flag.assert_called()

def test_handle_load_analysis_success(mock_controller, mock_state_manager):
    mc = MainContent(mock_controller)
    mock_controller.handle_load_analysis.return_value = (True, "DF", None)
    
    mc._handle_load_analysis("analysis_1")
    
    mock_state_manager.set_loaded_analysis.assert_called_with("analysis_1", "DF")

def test_render_analysis_display(mock_controller, mock_state_manager, mock_components, mock_streamlit):
    mc = MainContent(mock_controller)
    
    # Mock return of get_current_analysis
    import pandas as pd
    df = pd.DataFrame({'a': [1]})
    mock_state_manager.get_current_analysis.return_value = df
    mock_state_manager.get_current_analysis_name.return_value = "Test Analysis"
    
    # Mock prepare_analysis_display
    mock_controller.prepare_analysis_display.return_value = (df, {})
    
    # Mock table component returning no changes
    mock_components['table'].render_editable.return_value = (df, False)
    
    mc._render_analysis_display()
    
    # Check components rendering
    mock_components['charts'].render.assert_called()
    mock_components['wc'].render.assert_called()
    mock_components['table'].render_editable.assert_called()
    mock_components['export'].render.assert_called()

def test_handle_sentiment_update_success(mock_controller, mock_state_manager, mock_streamlit):
    mc = MainContent(mock_controller)
    
    analysis_name = "test"
    original_df = pd.DataFrame({'Clasificacion': ['Neutro']}, index=[0])
    edited_df = pd.DataFrame({'Clasificación': ['Promotor']}, index=[0]) # Renamed as in UI
    
    mock_state_manager.get_current_analysis.return_value = original_df
    mock_controller.handle_update_sentiment.return_value = (True, "new_name", "Success")
    
    mc._handle_sentiment_update(analysis_name, original_df, edited_df)
    
    mock_controller.handle_update_sentiment.assert_called()
    mock_streamlit.success.assert_called()
    mock_streamlit.rerun.assert_called()
