import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from adapters.file_readers.file_reader_adapter import PandasFileReader

class MockFile:
    pass

def test_read_csv():
    reader = PandasFileReader()
    file_obj = MockFile()
    
    with patch('pandas.read_csv') as mock_read:
        expected_df = pd.DataFrame({'a': [1]})
        mock_read.return_value = expected_df
        
        result = reader.read_file(file_obj, "text/csv")
        
        assert result.equals(expected_df)
        mock_read.assert_called_with(file_obj)

def test_read_csv_error():
    reader = PandasFileReader()
    with patch('pandas.read_csv') as mock_read:
        mock_read.side_effect = Exception("Read Error")
        with pytest.raises(ValueError, match="Error al leer el archivo CSV"):
            reader.read_file(MockFile(), "text/csv")

def test_read_excel_success():
    reader = PandasFileReader(required_sheets=["Sheet1"])
    file_obj = MockFile()
    
    with patch('pandas.read_excel') as mock_read:
        # Return dict of sheets
        mock_read.return_value = {
            "Sheet1": pd.DataFrame({'a': [1]}),
            "Sheet2": pd.DataFrame({'b': [2]})
        }
        
        result = reader.read_file(file_obj, "application/vnd.ms-excel")
        
        # Should concat only Sheet1
        assert len(result) == 1
        assert result['a'].iloc[0] == 1
        assert 'b' not in result.columns

def test_read_excel_missing_sheets():
    reader = PandasFileReader(required_sheets=["Required"])
    file_obj = MockFile()
    
    with patch('pandas.read_excel') as mock_read:
        mock_read.return_value = {"Other": pd.DataFrame()}
        
        with pytest.raises(ValueError, match="No se encontraron las hojas requeridas"):
            reader.read_file(file_obj, "application/vnd.ms-excel")

def test_read_excel_error():
    reader = PandasFileReader()
    with patch('pandas.read_excel') as mock_read:
        mock_read.side_effect = Exception("Excel Error")
        with pytest.raises(ValueError, match="Error al leer el archivo Excel"):
            reader.read_file(MockFile(), "application/vnd.ms-excel")

def test_unsupported_file_type():
    reader = PandasFileReader()
    with pytest.raises(ValueError, match="Tipo de archivo no soportado"):
        reader.read_file(MockFile(), "image/png")
