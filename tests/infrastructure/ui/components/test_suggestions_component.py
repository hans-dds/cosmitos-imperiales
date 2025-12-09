import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from infrastructure.ui.components.suggestions_component import SuggestionsComponent

@pytest.fixture
def mock_use_case():
    return MagicMock()

@pytest.fixture
def mock_streamlit():
    with patch('infrastructure.ui.components.suggestions_component.st') as mock:
        yield mock

def test_render_no_interaction(mock_use_case, mock_streamlit):
    comp = SuggestionsComponent(mock_use_case)
    df = pd.DataFrame()
    
    # Mock button returning False (not clicked)
    mock_streamlit.button.return_value = False
    
    comp.render(df)
    
    mock_streamlit.button.assert_called_with("Generar Recomendaciones Estratégicas", type="primary")
    mock_use_case.execute.assert_not_called()

def test_render_click_success_with_suggestions(mock_use_case, mock_streamlit):
    comp = SuggestionsComponent(mock_use_case)
    df = pd.DataFrame()
    
    mock_streamlit.button.return_value = True
    
    # Mock suggestions
    suggestions = [
        {"tema": "Tiempos de espera", "sugerencia": "Contratar más personal"},
        {"tema": "Calidad", "sugerencia": "Revisar proveedores"}
    ]
    mock_use_case.execute.return_value = suggestions
    
    # Mock columns
    col1, col2 = MagicMock(), MagicMock()
    mock_streamlit.columns.return_value = [col1, col2]
    
    comp.render(df)
    
    mock_use_case.execute.assert_called_with(df)
    # Check that columns were created
    mock_streamlit.columns.assert_called_with(2)
    # We can't easily check what happened inside the `with cols[i]` context managers 
    # without complex mocking of __enter__, but we can verified calls exist.
    assert col1.__enter__.called
    assert col2.__enter__.called

def test_render_click_success_no_suggestions(mock_use_case, mock_streamlit):
    comp = SuggestionsComponent(mock_use_case)
    df = pd.DataFrame()
    
    mock_streamlit.button.return_value = True
    mock_use_case.execute.return_value = []
    
    comp.render(df)
    
    mock_use_case.execute.assert_called_with(df)
    mock_streamlit.success.assert_called()

def test_render_click_error(mock_use_case, mock_streamlit):
    comp = SuggestionsComponent(mock_use_case)
    df = pd.DataFrame()
    
    mock_streamlit.button.return_value = True
    mock_use_case.execute.side_effect = Exception("AI Error")
    
    comp.render(df)
    
    mock_streamlit.error.assert_called_with("Error en análisis: AI Error")
