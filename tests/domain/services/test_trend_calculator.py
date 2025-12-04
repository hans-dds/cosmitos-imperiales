import pytest
import pandas as pd
from domain.services.trend_calculator import (
    calculate_average_trend,
    calculate_sentiment_distribution_trend,
    calculate_trend_change
)


@pytest.fixture
def sample_data():
    """Creates a sample DataFrame for testing."""
    data = {
        'fecha': [
            '2023-01-01', '2023-01-15',
            '2023-02-01', '2023-02-15',
            '2023-03-01'
        ],
        'calificacion': [8.0, 9.0, 7.0, 6.0, 10.0],
        'Clasificacion': [
            'Positivo', 'Positivo',
            'Neutro', 'Negativo',
            'Positivo'
        ]
    }
    df = pd.DataFrame(data)
    df['fecha'] = pd.to_datetime(df['fecha'])
    return df


class TestTrendCalculator:

    def test_calculate_average_trend_monthly(self, sample_data):
        """Test monthly average calculation."""
        result = calculate_average_trend(sample_data, frequency='M')

        assert len(result) == 3
        # Jan average: (8+9)/2 = 8.5
        assert result.iloc[0]['calificacion'] == 8.5
        # Feb average: (7+6)/2 = 6.5
        assert result.iloc[1]['calificacion'] == 6.5
        # Mar average: 10.0
        assert result.iloc[2]['calificacion'] == 10.0

    def test_calculate_average_trend_empty(self):
        """Test with empty dataframe."""
        df = pd.DataFrame()
        result = calculate_average_trend(df)
        assert result.empty

    def test_calculate_average_trend_missing_columns(self):
        """Test with missing required columns."""
        df = pd.DataFrame({'other': [1, 2, 3]})
        result = calculate_average_trend(df)
        assert result.empty

    def test_calculate_sentiment_distribution_trend(self, sample_data):
        """Test sentiment distribution calculation."""
        result = calculate_sentiment_distribution_trend(
            sample_data, frequency='M')

        # Check January (2 Positives)
        jan_data = result[result['fecha'] == '2023-01-31']
        assert not jan_data.empty
        # Should be 100% positive
        positive_jan = jan_data[jan_data['Clasificacion'] == 'Positivo']
        assert positive_jan.iloc[0]['porcentaje'] == 100.0

        # Check February (1 Neutro, 1 Negativo)
        feb_data = result[result['fecha'] == '2023-02-28']
        assert len(feb_data) == 2
        assert feb_data[
            feb_data['Clasificacion'] == 'Neutro'
        ].iloc[0]['porcentaje'] == 50.0
        assert feb_data[
            feb_data['Clasificacion'] == 'Negativo'
        ].iloc[0]['porcentaje'] == 50.0

    def test_calculate_trend_change(self):
        """Test trend change calculation."""
        data = {
            'fecha': ['2023-01-31', '2023-02-28'],
            'calificacion': [8.0, 6.0]
        }
        df = pd.DataFrame(data)

        last, prev, delta = calculate_trend_change(df)

        assert last == 6.0
        assert prev == 8.0
        assert delta == -2.0

    def test_calculate_trend_change_insufficient_data(self):
        """Test trend change with insufficient data."""
        data = {
            'fecha': ['2023-01-31'],
            'calificacion': [8.0]
        }
        df = pd.DataFrame(data)

        last, prev, delta = calculate_trend_change(df)

        assert last is None
        assert prev is None
        assert delta is None
