import pytest
import pandas as pd
from domain.services.metrics_calculator import (
    calculate_comment_length,
    calculate_summary_metrics,
)

def test_calculate_comment_length_adds_column():
    df = pd.DataFrame({'comentarios': ['hola', 'mundo', '']})
    result = calculate_comment_length(df)
    
    assert 'longitud' in result.columns
    assert result['longitud'].tolist() == [4, 5, 0]

def test_calculate_comment_length_missing_column():
    df = pd.DataFrame({'other': [1, 2]})
    result = calculate_comment_length(df)
    assert 'longitud' not in result.columns
    pd.testing.assert_frame_equal(result, df)

def test_calculate_comment_length_existing_column():
    # Should not overwrite if logic changes, but current logic DOES overwrite/recalc
    # primarily checking it doesn't error
    df = pd.DataFrame({'comentarios': ['a'], 'longitud': [999]})
    result = calculate_comment_length(df)
    assert result['longitud'].iloc[0] == 999

def test_calculate_summary_metrics_success():
    df = pd.DataFrame({
        'Clasificacion': ['A', 'A', 'B'],
        'comentarios': ['xx', 'yyyy', 'z']
    })
    # Lengths: A: 2, 4 (avg 3). B: 1 (avg 1)
    # Total: 3. A%=66.67, B%=33.33
    
    summary = calculate_summary_metrics(df)
    
    assert not summary.empty
    assert 'Clasificacion' in summary.columns
    assert 'NumComentarios' in summary.columns
    assert 'LongitudPromedio' in summary.columns
    assert 'Porcentaje' in summary.columns
    
    row_a = summary[summary['Clasificacion'] == 'A'].iloc[0]
    assert row_a['NumComentarios'] == 2
    assert row_a['LongitudPromedio'] == 3.0
    assert row_a['Porcentaje'] == 66.67
    
    row_b = summary[summary['Clasificacion'] == 'B'].iloc[0]
    assert row_b['NumComentarios'] == 1
    assert row_b['LongitudPromedio'] == 1.0
    assert row_b['Porcentaje'] == 33.33

def test_calculate_summary_metrics_empty():
    df = pd.DataFrame()
    summary = calculate_summary_metrics(df)
    assert summary.empty

def test_calculate_summary_metrics_missing_classification():
    df = pd.DataFrame({'comentarios': ['asd']})
    summary = calculate_summary_metrics(df)
    assert summary.empty

def test_calculate_summary_metrics_with_precalculated_length():
    df = pd.DataFrame({
        'Clasificacion': ['A'],
        'comentarios': ['ignored'],
        'longitud': [100]
    })
    summary = calculate_summary_metrics(df)
    
    # Logic: if 'longitud' exists, it uses it for mean
    assert summary.iloc[0]['LongitudPromedio'] == 100.0
