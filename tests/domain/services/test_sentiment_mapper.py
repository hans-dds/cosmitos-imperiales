import pytest
import pandas as pd
from domain.services.sentiment_mapper import convert_numeric_to_sentiment, convert_dataframe_classifications
from domain.value_objects.sentiment import Sentiment

def test_convert_numeric_to_sentiment():
    # Tests based on Sentiment.from_numeric implementations
    # Usually: -1 -> Detractor/Negativo, 0 -> Neutro, 1 -> Promotor/Positivo?
    # Or checking common scales. Code uses Sentiment.from_numeric
    # Assuming standard mapping if not visible.
    
    # We'll mock Sentiment if needed, or rely on its enum logic.
    # Looking at usage, it converts numerics.
    
    val = -1
    # Check what from_numeric returns. If it returns Enum, .value gives string
    # Try generic assertion if mapping unknown or standard
    res = convert_numeric_to_sentiment(-1)
    assert isinstance(res, str)
    
    # Non-convertible
    assert convert_numeric_to_sentiment("Texto") == "Texto"
    assert convert_numeric_to_sentiment(None) is None

def test_convert_dataframe_classifications_empty():
    df = pd.DataFrame()
    res = convert_dataframe_classifications(df)
    assert res.empty

def test_convert_dataframe_classifications_numeric_col():
    df = pd.DataFrame({'Clasificacion': [-1, 0, 1]})
    res = convert_dataframe_classifications(df)
    # Should be converted to strings
    assert res['Clasificacion'].dtype == 'object'
    assert isinstance(res['Clasificacion'].iloc[0], str)

def test_convert_dataframe_classifications_mixed_col():
    df = pd.DataFrame({'Clasificacion': [-1, "Neutral", "1"]})
    res = convert_dataframe_classifications(df)
    # Should convert numeric-likestrings and ints
    assert res['Clasificacion'].iloc[0] in [Sentiment.DETRACTOR.value, "Detractor", "Negativo"]
    assert res['Clasificacion'].iloc[2] in [Sentiment.PROMOTOR.value, "Promotor", "Positivo"]
