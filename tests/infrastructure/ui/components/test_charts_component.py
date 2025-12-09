import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from infrastructure.ui.components.charts_component import ChartsComponent


@pytest.fixture
def mock_streamlit():
    with patch('infrastructure.ui.components.charts_component.st') as mock:
        mock.columns.return_value = [MagicMock(), MagicMock()]
        yield mock


@pytest.fixture
def mock_plotly():
    with patch('infrastructure.ui.components.charts_component.px') as mock:
        yield mock


def test_validate_data_missing_cols(mock_streamlit):
    comp = ChartsComponent()
    df = pd.DataFrame({'a': [1]})
    comp.render(df, {})

    mock_streamlit.error.assert_called()
    assert "no tiene las columnas requeridas" in mock_streamlit.error.call_args[0][0]


def test_render_success(mock_streamlit, mock_plotly):
    comp = ChartsComponent()
    df = pd.DataFrame({
        'comentarios': ['a', 'b'],
        'Clasificacion': ['Neutro', 'Promotor']
    })

    comp.render(df, {})

    # Check if sub-renders were called indirectly via plotly calls
    assert mock_plotly.pie.called
    assert mock_plotly.bar.called
    assert mock_plotly.histogram.called

    # Check streamlit chart calls
    assert mock_streamlit.plotly_chart.call_count >= 3  # Pie, Bar, Hist


def test_render_evolution_no_date(mock_streamlit, mock_plotly):
    comp = ChartsComponent()
    df = pd.DataFrame({
        'comentarios': ['a'],
        'Clasificacion': ['Neutro'],
        'longitud': [1]
    })

    comp._render_evolution_chart(df, {})

    mock_streamlit.info.assert_called_with("Este análisis no contiene información de fechas.")


def test_render_evolution_one_date_only(mock_streamlit, mock_plotly):
    comp = ChartsComponent()
    df = pd.DataFrame({
        'comentarios': ['a', 'b'],
        'Clasificacion': ['Neutro', 'Neutro'],
        'fecha': [pd.Timestamp('2023-01-01'), pd.Timestamp('2023-01-01')]
    })

    comp._render_evolution_chart(df, {})

    # Should warn about insufficient data (need >1 unique date)
    assert "no contiene información suficiente" in mock_streamlit.info.call_args_list[0][0][0]


def test_render_evolution_success(mock_streamlit, mock_plotly):
    comp = ChartsComponent()
    # Need >1 unique date
    df = pd.DataFrame({
        'comentarios': ['a', 'b'],
        'calificacion': [5, 1],
        'Clasificacion': ['Promotor', 'Detractor'],
        'fecha': [pd.Timestamp('2023-01-01'), pd.Timestamp('2023-02-01')]
    })

    mock_streamlit.selectbox.return_value = "Mensual"

    with patch(
        'infrastructure.ui.components.charts_component.calculate_average_trend'
    ) as mock_avg, patch(
        'infrastructure.ui.components.charts_component.calculate_sentiment_distribution_trend'
    ) as mock_dist, patch(
        'infrastructure.ui.components.charts_component.calculate_trend_change'
    ) as mock_change:

        # Setup mocks returning valid DFs
        mock_avg.return_value = pd.DataFrame({
            'fecha': [pd.Timestamp('2023-01-01')], 'calificacion': [3.0]
        })
        mock_dist.return_value = pd.DataFrame({
            'fecha': [pd.Timestamp('2023-01-01')], 'porcentaje': [100], 'Clasificacion': ['Neutro']
        })
        mock_change.return_value = (3.0, 0.0, 0.0)

        comp._render_evolution_chart(df, {})

        assert mock_streamlit.metric.called
        assert mock_plotly.line.called
        assert mock_plotly.area.called
