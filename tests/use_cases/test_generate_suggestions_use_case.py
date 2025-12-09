import pytest
import pandas as pd
from unittest.mock import MagicMock
from use_cases.generate_suggestions_use_case import GenerateSuggestionsUseCase
from domain.value_objects.sentiment import Sentiment

@pytest.fixture
def mock_generator():
    return MagicMock()

def test_execute_empty_dataframe(mock_generator):
    uc = GenerateSuggestionsUseCase(mock_generator)
    result = uc.execute(pd.DataFrame())
    assert result == []
    mock_generator.generate.assert_not_called()

def test_execute_no_classification_column(mock_generator):
    uc = GenerateSuggestionsUseCase(mock_generator)
    result = uc.execute(pd.DataFrame({"other": [1]}))
    assert result == []
    mock_generator.generate.assert_not_called()

def test_execute_no_detractors(mock_generator):
    uc = GenerateSuggestionsUseCase(mock_generator)
    df = pd.DataFrame({
        "Clasificacion": ["Promotor", "Neutro"],
        "comentarios": ["Good", "Okay"]
    })
    result = uc.execute(df)
    assert result == []
    mock_generator.generate.assert_not_called()

def test_execute_detractors_found(mock_generator):
    uc = GenerateSuggestionsUseCase(mock_generator)
    # Test both string "Detractor" and enum value if possible
    # The code uses: (df["Clasificacion"] == Sentiment.DETRACTOR.value) | (df["Clasificacion"] == "Detractor")
    
    df = pd.DataFrame({
        "Clasificacion": ["Detractor", "Promotor", Sentiment.DETRACTOR.value],
        "comentarios": ["Bad1", "Good", "Bad2"]
    })
    
    expected_suggestions = [{"tema": "t1", "sugerencia": "s1"}]
    mock_generator.generate.return_value = expected_suggestions
    
    result = uc.execute(df)
    
    assert result == expected_suggestions
    # Verify generate called with only detractor comments
    # Pandas filtering might preserve index order or not, usually does.
    # Bad1 is Detractor, Bad2 is Sentiment.DETRACTOR.value (which is "Detractor" usually)
    mock_generator.generate.assert_called()
    args = mock_generator.generate.call_args[0][0]
    assert "Bad1" in args
    assert "Bad2" in args
    assert "Good" not in args
