import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import MagicMock
from use_cases.process_file_use_case import ProcessFileUseCase


@pytest.fixture
def mock_cleaner():
    return MagicMock()


@pytest.fixture
def mock_analyzer():
    return MagicMock()


@pytest.fixture
def mock_repository():
    return MagicMock()


def test_execute_success(mock_cleaner, mock_analyzer, mock_repository):
    uc = ProcessFileUseCase(mock_cleaner, mock_analyzer, mock_repository)
    raw_df = pd.DataFrame({'raw': [1]})
    cleaned_df = pd.DataFrame({'cleaned': [1]})
    analyzed_df = pd.DataFrame({'cleaned': [1], 'sentiment': ['pos']})

    mock_cleaner.clean_data.return_value = cleaned_df
    mock_analyzer.analyze.return_value = analyzed_df

    result = uc.execute(raw_df, "archivo_Enero_2023")

    mock_cleaner.clean_data.assert_called_with(raw_df)
    mock_analyzer.analyze.assert_called_with(cleaned_df)
    # Check date extraction logic added 'fecha'
    assert 'fecha' in result.columns
    assert result['fecha'].iloc[0] == datetime(2023, 1, 1)

    mock_repository.save.assert_called_with(result, "archivo_Enero_2023")


def test_execute_cleaner_returns_empty(mock_cleaner, mock_analyzer, mock_repository):
    uc = ProcessFileUseCase(mock_cleaner, mock_analyzer, mock_repository)
    mock_cleaner.clean_data.return_value = pd.DataFrame()

    with pytest.raises(ValueError, match="vacíos después del proceso de limpieza"):
        uc.execute(pd.DataFrame(), "file")


def test_execute_analyzer_returns_empty(mock_cleaner, mock_analyzer, mock_repository):
    uc = ProcessFileUseCase(mock_cleaner, mock_analyzer, mock_repository)
    mock_cleaner.clean_data.return_value = pd.DataFrame({'data': [1]})
    mock_analyzer.analyze.return_value = pd.DataFrame()

    with pytest.raises(ValueError, match="vacíos después del análisis de sentimiento"):
        uc.execute(pd.DataFrame(), "file")


def test_date_extraction_logic(mock_cleaner, mock_analyzer, mock_repository):
    uc = ProcessFileUseCase(mock_cleaner, mock_analyzer, mock_repository)

    # Valid
    assert uc._extract_month_year_from_basename("c_Enero_2023") == datetime(2023, 1, 1)
    assert uc._extract_month_year_from_basename("c_Marzo_2024") == datetime(2024, 3, 1)

    # Invalid
    assert uc._extract_month_year_from_basename("invalid") is None
    assert uc._extract_month_year_from_basename("c_NotAMonth_2023") is None
    assert uc._extract_month_year_from_basename("c_Enero_NotAYear") is None
