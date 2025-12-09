import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from adapters.gemini_adapter import GeminiAdvisorAdapter

@pytest.fixture
def mock_genai():
    with patch('adapters.gemini_adapter.genai') as mock:
        yield mock

def test_init_with_key(mock_genai):
    adapter = GeminiAdvisorAdapter("fake_key")
    mock_genai.configure.assert_called_with(api_key="fake_key")
    mock_genai.GenerativeModel.assert_called_with("gemini-2.5-flash")
    assert adapter.model is not None

def test_init_without_key(mock_genai):
    adapter = GeminiAdvisorAdapter("")
    mock_genai.configure.assert_not_called()
    assert adapter.model is None

def test_analyze_no_model(mock_genai):
    adapter = GeminiAdvisorAdapter("") # No key -> no model
    df = pd.DataFrame()
    result = adapter.analyze_detractors(df)
    assert "Error: API Key de Gemini no configurada" in result

def test_analyze_missing_column(mock_genai):
    adapter = GeminiAdvisorAdapter("key")
    df = pd.DataFrame({'other': [1]})
    result = adapter.analyze_detractors(df)
    assert "No se encontró columna de calificación" in result

def test_analyze_no_detractors(mock_genai):
    adapter = GeminiAdvisorAdapter("key")
    # Assuming threshold is <= 6 for detractors
    df = pd.DataFrame({'calificacion': [7, 8, 9, 10], 'comentarios': ['ok']*4})
    result = adapter.analyze_detractors(df)
    assert "¡Excelente trabajo!" in result

def test_analyze_success(mock_genai):
    adapter = GeminiAdvisorAdapter("key")
    
    # Mock model generation
    mock_response = MagicMock()
    mock_response.text = "Sugerencias generadas"
    adapter.model.generate_content.return_value = mock_response
    
    df = pd.DataFrame({
        'calificacion': [1, 5, 10],
        'comentarios': ['Bad', 'Mediocre', 'Good']
    })
    
    result = adapter.analyze_detractors(df)
    
    assert result == "Sugerencias generadas"
    adapter.model.generate_content.assert_called()
    args = adapter.model.generate_content.call_args[0][0]
    assert "Bad" in args
    assert "Mediocre" in args
    assert "Good" not in args

def test_analyze_api_error(mock_genai):
    adapter = GeminiAdvisorAdapter("key")
    adapter.model.generate_content.side_effect = Exception("API Fail")
    
    df = pd.DataFrame({'calificacion': [1], 'comentarios': ['Bad']})
    result = adapter.analyze_detractors(df)
    
    assert "Error al consultar Gemini: API Fail" in result
