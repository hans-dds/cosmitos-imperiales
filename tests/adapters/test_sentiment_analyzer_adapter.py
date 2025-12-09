import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from adapters.sentiment_analyzer_adapter import JoblibSentimentAnalyzer
from domain.value_objects.sentiment import Sentiment

@pytest.fixture
def mock_joblib():
    with patch('adapters.sentiment_analyzer_adapter.joblib') as mock:
        yield mock

def test_init_load_success(mock_joblib):
    analyzer = JoblibSentimentAnalyzer('model.pkl')
    mock_joblib.load.assert_called_with('model.pkl')

def test_init_load_file_not_found(mock_joblib):
    mock_joblib.load.side_effect = FileNotFoundError
    with pytest.raises(RuntimeError, match="CRÍTICO: No se encontró el archivo"):
        JoblibSentimentAnalyzer('model.pkl')

def test_analyze_empty_df(mock_joblib):
    analyzer = JoblibSentimentAnalyzer('model.pkl')
    df = pd.DataFrame({'comentarios': [], 'calificacion': []})
    result = analyzer.analyze(df)
    assert result.empty

def test_analyze_success(mock_joblib):
    # Setup mock model
    model_mock = MagicMock()
    # Predictions: 1 (Promotor), -1 (Detractor), 0 (Neutro)
    model_mock.predict.return_value = [1, -1, 0]
    # Probabilities: for 3 classes
    # Item 1: class 2 is max (0.9)
    # Item 2: class 0 is max (0.8)
    # Item 3: class 1 is max (0.6)
    model_mock.predict_proba.return_value = pd.DataFrame([
        [0.05, 0.05, 0.9],
        [0.8, 0.1, 0.1],
        [0.2, 0.6, 0.2]
    ]).values 
    
    mock_joblib.load.return_value = model_mock
    
    analyzer = JoblibSentimentAnalyzer('model.pkl')
    
    df = pd.DataFrame({
        'comentarios': ['Great', 'Bad', 'Ok'],
        'calificacion': [5, 1, 3]
    })
    
    result = analyzer.analyze(df)
    
    assert 'Clasificacion' in result.columns
    assert 'Fiabilidad' in result.columns
    
    # Check classifications
    assert result.iloc[0]['Clasificacion'] == Sentiment.PROMOTOR.value
    assert result.iloc[1]['Clasificacion'] == Sentiment.DETRACTOR.value
    assert result.iloc[2]['Clasificacion'] == Sentiment.NEUTRAL.value
    
    # Check reliability (mocked calc check? Or assume logic works)
    # 0.9 -> High reliability
    # 0.6 -> Lower reliability

def test_analyze_no_proba_fallback(mock_joblib):
    model_mock = MagicMock()
    model_mock.predict.return_value = [1]
    # Delete predict_proba attribute to simulate model without it
    del model_mock.predict_proba
    
    mock_joblib.load.return_value = model_mock
    analyzer = JoblibSentimentAnalyzer('model.pkl')
    
    df = pd.DataFrame({'comentarios': ['A'], 'calificacion': [5]})
    result = analyzer.analyze(df)
    
    assert 'Fiabilidad' in result.columns
    # Should use rating fallback. 5 stars -> High reliability usually?
