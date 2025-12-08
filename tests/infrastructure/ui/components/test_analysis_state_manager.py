import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
from infrastructure.ui.components.analysis_state_manager import AnalysisStateManager

class MockSessionState(dict):
    """Mock Streamlit SessionState allowing attribute access."""
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError(key)

@pytest.fixture
def mock_session_state():
    """Mock streamlit.session_state as a dictionary with attribute access."""
    mock_state = MockSessionState()
    with patch('infrastructure.ui.components.analysis_state_manager.st.session_state', mock_state):
        yield mock_state

def test_initialize_state_sets_defaults(mock_session_state):
    # Ensure state starts empty for the test
    mock_session_state.clear()
    
    AnalysisStateManager.initialize_state()
    
    assert mock_session_state['selected_analysis'] is None
    assert mock_session_state['last_loaded_analysis'] is None
    assert mock_session_state['analysis_name'] is None
    assert mock_session_state['analyses_to_delete'] == []
    assert mock_session_state['confirm_delete'] is False

def test_initialize_state_preserves_existing(mock_session_state):
    mock_session_state['selected_analysis'] = 'existing'
    
    AnalysisStateManager.initialize_state()
    
    assert mock_session_state['selected_analysis'] == 'existing'

def test_set_new_analysis(mock_session_state):
    df = pd.DataFrame({'a': [1]})
    AnalysisStateManager.set_new_analysis("new_analysis", df, "file_id_123")
    
    assert mock_session_state['selected_analysis'] == "new_analysis"
    assert mock_session_state['last_loaded_analysis'] == "new_analysis"
    assert mock_session_state['analysis_name'] == "new_analysis"
    assert mock_session_state['last_processed_file'] == "file_id_123"
    pd.testing.assert_frame_equal(mock_session_state['df_display'], df)

def test_set_loaded_analysis(mock_session_state):
    df = pd.DataFrame({'b': [2]})
    AnalysisStateManager.set_loaded_analysis("loaded_analysis", df)
    
    assert mock_session_state['analysis_name'] == "loaded_analysis"
    assert mock_session_state['last_loaded_analysis'] == "loaded_analysis"
    pd.testing.assert_frame_equal(mock_session_state['df_display'], df)

def test_clear_analysis_display(mock_session_state):
    mock_session_state['df_display'] = "something"
    AnalysisStateManager.clear_analysis_display()
    assert 'df_display' not in mock_session_state

def test_clear_delete_selection(mock_session_state):
    mock_session_state['analyses_to_delete'] = ['a']
    mock_session_state['confirm_delete'] = True
    
    AnalysisStateManager.clear_delete_selection()
    
    assert mock_session_state['analyses_to_delete'] == []
    assert mock_session_state['confirm_delete'] is False

def test_get_current_analysis(mock_session_state):
    df = pd.DataFrame({'c': [3]})
    mock_session_state['df_display'] = df
    
    result = AnalysisStateManager.get_current_analysis()
    
    pd.testing.assert_frame_equal(result, df)

def test_get_current_analysis_none(mock_session_state):
    assert AnalysisStateManager.get_current_analysis() is None

def test_get_current_analysis_name(mock_session_state):
    mock_session_state['analysis_name'] = "test_name"
    assert AnalysisStateManager.get_current_analysis_name() == "test_name"

def test_needs_load_explicit(mock_session_state):
    assert AnalysisStateManager.needs_load("explicit_load") is True

def test_needs_load_change_selection(mock_session_state):
    # Selected analysis changed in sidebar, but not yet loaded
    mock_session_state['selected_analysis'] = "new_selection"
    mock_session_state['last_loaded_analysis'] = "old_selection"
    mock_session_state['analysis_name'] = "old_selection"
    
    assert AnalysisStateManager.needs_load(None) is True

def test_needs_load_same_selection(mock_session_state):
    # Selected same as loaded
    mock_session_state['selected_analysis'] = "current"
    mock_session_state['last_loaded_analysis'] = "current"
    mock_session_state['analysis_name'] = "current"
    
    assert AnalysisStateManager.needs_load(None) is False

def test_is_file_already_processed(mock_session_state):
    mock_session_state['last_processed_file'] = "file_123"
    assert AnalysisStateManager.is_file_already_processed("file_123") is True
    assert AnalysisStateManager.is_file_already_processed("file_456") is False

def test_clear_processed_file_flag(mock_session_state):
    mock_session_state['last_processed_file'] = "file_123"
    AnalysisStateManager.clear_processed_file_flag()
    assert 'last_processed_file' not in mock_session_state
