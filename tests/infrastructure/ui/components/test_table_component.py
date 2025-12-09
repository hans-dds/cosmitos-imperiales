import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from infrastructure.ui.components.table_component import TableComponent

@pytest.fixture
def mock_streamlit():
    with patch('infrastructure.ui.components.table_component.st') as mock:
        # Defaults for session state
        mock.session_state = {}
        # Columns context manager mock
        col1, col2, col3 = MagicMock(), MagicMock(), MagicMock()
        mock.columns.return_value = [col1, col2, col3]
        # Slider must return int for dataframe slicing
        mock.slider.return_value = 10
        yield mock

def test_validate_columns_missing(mock_streamlit):
    comp = TableComponent()
    df = pd.DataFrame({'a': [1]}) # Missing required cols
    
    # We can test private method via public render call or directly if needed, 
    # but render protects itself.
    comp.render(df)
    
    mock_streamlit.warning.assert_called()
    assert "Faltan las columnas" in mock_streamlit.warning.call_args[0][0]

def test_validate_columns_adds_reliability(mock_streamlit):
    comp = TableComponent()
    # Required: calificacion, comentarios, Clasificacion
    df = pd.DataFrame({
        'calificacion': [5],
        'comentarios': ['ok'],
        'Clasificacion': ['Neutro']
    })
    
    # render calls _validate_columns which adds Fiabilidad if missing
    # render also filters and calls dataframe, so we check if the df passed to dataframe has it
    comp.render(df)
    
    # Check what was passed to dataframe
    assert mock_streamlit.dataframe.called
    df_displayed = mock_streamlit.dataframe.call_args[0][0]
    # Check column renaming applied ("Fiabilidad" -> "Fiabilidad")
    assert "Fiabilidad" in df_displayed.columns or "Fiabilidad" in mock_streamlit.dataframe.call_args[0][0].columns

def test_apply_filters_category(mock_streamlit):
    comp = TableComponent()
    df = pd.DataFrame({
        'calificacion': [1, 5],
        'comentarios': ['bad', 'good'],
        'Clasificacion': ['Detractor', 'Promotor'],
        'Fiabilidad': ['Alta', 'Alta']
    })
    
    # Mock session state to select 'Promotor'
    # We need to ensure that the selectbox return value matches what we want
    mock_streamlit.selectbox.return_value = "Promotor" # For category filter
    # Note: selectbox is called multiple times (category, sort field). 
    # We might need side_effect if we want distinct values. 
    # First call is category, second is sort field.
    mock_streamlit.selectbox.side_effect = ["Promotor", "Sin ordenar"]
    
    comp.render(df)
    
    df_displayed = mock_streamlit.dataframe.call_args[0][0]
    # Should only have 1 row (Promotor)
    assert len(df_displayed) == 1
    # Check contents indirectly via knowing only 1 row remains
    
    # Verify session state update
    assert mock_streamlit.session_state["comments_filter_category"] == "Promotor"

def test_apply_filters_sort(mock_streamlit):
    comp = TableComponent()
    df = pd.DataFrame({
        'calificacion': [1, 5],
        'comentarios': ['a', 'b'],
        'Clasificacion': ['Detractor', 'Promotor'],
        'Fiabilidad': ['Alta', 'Alta']
    })
    
    # 1. Category: Todas
    # 2. Sort: Calificación
    mock_streamlit.selectbox.side_effect = ["Todas", "Calificación"]
    # Radio: Descendente (default index 1)
    mock_streamlit.radio.return_value = "Descendente"
    
    comp.render(df)
    
    # Should sort by calificacion descending -> 5 then 1
    df_displayed = mock_streamlit.dataframe.call_args[0][0]
    # In render, we rename columns. Calificacion -> Calificación (with accent)
    assert df_displayed.iloc[0]['Calificación'] == 5

def test_render_editable_no_changes(mock_streamlit):
    comp = TableComponent()
    df = pd.DataFrame({
        'calificacion': [5],
        'comentarios': ['ok'],
        'Clasificacion': ['Promotor'],
        'Fiabilidad': ['Alta']
    })
    
    # Setup mocks
    mock_streamlit.selectbox.side_effect = ["Todas", "Sin ordenar"]
    mock_streamlit.slider.return_value = 10
    
    # Mock data_editor returning same df
    mock_streamlit.data_editor.return_value = df.rename(columns={
        'calificacion': 'Calificación', 
        'comentarios': 'Comentario', 
        'Clasificacion': 'Clasificación',
        'Fiabilidad': 'Fiabilidad'
    })
    
    # Mock original state
    mock_streamlit.session_state["original_df_for_edit"] = mock_streamlit.data_editor.return_value
    
    edited_df, changes = comp.render_editable(df)
    
    assert changes is False
    assert not edited_df.empty

def test_render_editable_with_changes(mock_streamlit):
    comp = TableComponent()
    df = pd.DataFrame({
        'calificacion': [5],
        'comentarios': ['ok'],
        'Clasificacion': ['Promotor'],
        'Fiabilidad': ['Alta']
    })
    
    df_renamed = df.rename(columns={
        'calificacion': 'Calificación', 
        'comentarios': 'Comentario', 
        'Clasificacion': 'Clasificación',
        'Fiabilidad': 'Fiabilidad'
    })
    
    # Setup mocks
    mock_streamlit.selectbox.side_effect = ["Todas", "Sin ordenar"]
    mock_streamlit.slider.return_value = 10
    
    # Mock data_editor returning CHANGED df
    changed_df = df_renamed.copy()
    changed_df.at[0, 'Clasificación'] = 'Detractor'
    mock_streamlit.data_editor.return_value = changed_df
    
    # Mock original state
    mock_streamlit.session_state["original_df_for_edit"] = df_renamed
    
    edited_df, changes = comp.render_editable(df)
    
    assert changes is True
    assert edited_df.iloc[0]['Clasificación'] == 'Detractor'
