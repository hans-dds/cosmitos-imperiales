import pytest
import pandas as pd
from unittest.mock import MagicMock
from use_cases.update_sentiment_use_case import UpdateSentimentUseCase
from domain.value_objects.sentiment import Sentiment

@pytest.fixture
def mock_repository():
    return MagicMock()

def test_execute_success(mock_repository):
    uc = UpdateSentimentUseCase(mock_repository)
    df = pd.DataFrame({
        "Clasificacion": ["Positivo", "Negativo"],
        "Comentario": ["Bien", "Mal"]
    })
    
    modifications = [(0, "Neutro")] # Valid change
    
    mock_repository.clone_with_modifications.return_value = (True, "new_id", "Success")
    
    success, new_id, msg = uc.execute("orig_id", df, modifications)
    
    assert success is True
    assert new_id == "new_id"
    
    # Verify repository called with modified data
    args, _ = mock_repository.clone_with_modifications.call_args
    modified_df = kwargs.get('modified_data') if 'modified_data' in (kwargs := mock_repository.clone_with_modifications.call_args.kwargs) else args[1] 
    # Actually explicit args logic
    # args[0] might be original_id, args[1] modified_df if positional.
    # Keyword args safer.
    
    # Check call arguments more robustly
    call_kwargs = mock_repository.clone_with_modifications.call_args.kwargs
    modified_df = call_kwargs['modified_data']
    assert modified_df.iloc[0]["Clasificacion"] == "Neutro"

def test_execute_no_modifications(mock_repository):
    uc = UpdateSentimentUseCase(mock_repository)
    success, _, msg = uc.execute("id", pd.DataFrame(), [])
    assert success is False
    assert "No se proporcionaron modificaciones" in msg

def test_execute_missing_column(mock_repository):
    uc = UpdateSentimentUseCase(mock_repository)
    df = pd.DataFrame({"Other": [1]})
    
    success, _, msg = uc.execute("id", df, [(0, "Neutro")])
    assert success is False
    assert "no tiene la columna 'Clasificacion'" in msg

def test_execute_invalid_index(mock_repository):
    uc = UpdateSentimentUseCase(mock_repository)
    df = pd.DataFrame({"Clasificacion": ["Positivo"]})
    
    success, _, msg = uc.execute("id", df, [(99, "Neutro")])
    assert success is False
    assert "Índice 99 no existe" in msg

def test_execute_invalid_label(mock_repository):
    uc = UpdateSentimentUseCase(mock_repository)
    df = pd.DataFrame({"Clasificacion": ["Positivo"]})
    
    success, _, msg = uc.execute("id", df, [(0, "INVALIDO")])
    assert success is False
    assert "Etiqueta inválida" in msg

def test_execute_repo_failure(mock_repository):
    uc = UpdateSentimentUseCase(mock_repository)
    df = pd.DataFrame({"Clasificacion": ["Positivo"]})
    
    mock_repository.clone_with_modifications.return_value = (False, "", "DB Error")
    
    success, _, msg = uc.execute("id", df, [(0, "Neutro")])
    assert success is False
    assert "DB Error" in msg
