import pytest
from unittest.mock import MagicMock, patch
from infrastructure.ui.components.delete_analysis_component import DeleteAnalysisComponent

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
    with patch('infrastructure.ui.components.delete_analysis_component.st') as mock:
        mock.session_state = MockSessionState()
        mock.columns.return_value = [MagicMock(), MagicMock()]
        yield mock

def test_render_no_saved_analyses(mock_controller, mock_streamlit):
    comp = DeleteAnalysisComponent(mock_controller)
    comp.render([])
    # Should exit early
    assert not mock_streamlit.sidebar.expander.called
    assert not mock_streamlit.expander.called

def test_render_selection_flow(mock_controller, mock_streamlit):
    comp = DeleteAnalysisComponent(mock_controller)
    saved = ["analisis_1", "analisis_2"]
    
    # Mock multiselect returning "analisis_1"
    mock_streamlit.multiselect.return_value = ["analisis_1"]
    
    comp.render(saved)
    
    # Check session state update
    assert mock_streamlit.session_state["analyses_to_delete"] == ["analisis_1"]
    
    # Check button rendered (delete confirmation trigger)
    mock_streamlit.button.assert_called()

def test_delete_confirmation_execution_success(mock_controller, mock_streamlit):
    comp = DeleteAnalysisComponent(mock_controller)
    # Pre-set session state for confirmation
    mock_streamlit.session_state.analyses_to_delete = ["analisis_1"]
    mock_streamlit.session_state.confirm_delete = True
    
    # Mock deletion success
    mock_controller.handle_delete_multiple_analyses.return_value = (True, [("analisis_1", True, "Deleted")])
    
    # We need to simulate the "Confirm" button being clicked inside _show_confirmation_ui
    # The render triggers _render_delete_confirmation -> _show_confirmation_ui -> button("Confirmar")
    # We mock button return values. 
    # button calls: 1. "Cancel" (if present), 2. "Confirm"
    # Actually code has col1, col2. Order depends on execution.
    # Let's mock button to return True when key="confirm_delete_btn" is passed, else False
    def button_side_effect(*args, **kwargs):
        return kwargs.get("key") == "confirm_delete_btn"
    
    mock_streamlit.button.side_effect = button_side_effect
    
    comp._render_delete_confirmation(["analisis_1"])
    
    # Verify execution
    mock_controller.handle_delete_multiple_analyses.assert_called_with(["analisis_1"])
    mock_streamlit.success.assert_called()
    assert mock_streamlit.session_state["analyses_to_delete"] == []  # Cleared
    assert mock_streamlit.session_state["confirm_delete"] is False

def test_delete_confirmation_execution_failure(mock_controller, mock_streamlit):
    comp = DeleteAnalysisComponent(mock_controller)
    mock_streamlit.session_state.analyses_to_delete = ["analisis_1"]
    mock_streamlit.session_state.confirm_delete = True
    
    mock_controller.handle_delete_multiple_analyses.return_value = (False, [("analisis_1", False, "Error")])
    
    def button_side_effect(*args, **kwargs):
        return kwargs.get("key") == "confirm_delete_btn"
    mock_streamlit.button.side_effect = button_side_effect
    
    comp._render_delete_confirmation(["analisis_1"])
    
    mock_streamlit.warning.assert_called()  # Summary warning
    mock_streamlit.error.assert_called_with("❌ analisis_1: Error")
    # Clean up happens anyway in this implementation
    assert mock_streamlit.rerun.called
