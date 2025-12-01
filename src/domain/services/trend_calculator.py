"""
Servicio de dominio para calcular tendencias históricas.

Este módulo encapsula la lógica para agrupar datos por periodos de tiempo
(meses, trimestres) y calcular métricas como promedios y distribuciones.
"""

import pandas as pd
from typing import Optional, Tuple


def calculate_average_trend(
    df: pd.DataFrame,
    frequency: str = 'ME'
) -> pd.DataFrame:
    """
    Calcula la tendencia del promedio de calificación agrupada por fecha.

    Args:
        df: DataFrame con columnas 'fecha' y 'calificacion'.
        frequency: Frecuencia de agrupación ('M' mensual, 'Q' trimestral).

    Returns:
        DataFrame con columnas 'fecha' y 'calificacion' (promedio).
        Retorna DataFrame vacío si no hay datos o columnas requeridas.
    """
    if frequency == 'M':
        frequency = 'ME'

    if (df.empty or 'fecha' not in df.columns or
            'calificacion' not in df.columns):
        return pd.DataFrame()

    df = df.copy()
    # Asegurar tipos
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    df['calificacion'] = pd.to_numeric(df['calificacion'], errors='coerce')

    # Filtrar inválidos
    df = df.dropna(subset=['fecha', 'calificacion'])

    if df.empty:
        return pd.DataFrame()

    # Agrupar
    trend = df.groupby(
        pd.Grouper(key='fecha', freq=frequency)
    )['calificacion'].mean().reset_index()

    trend = trend.sort_values('fecha')
    trend = trend.dropna(subset=['calificacion'])

    return trend


def calculate_sentiment_distribution_trend(
    df: pd.DataFrame,
    frequency: str = 'ME'
) -> pd.DataFrame:
    """
    Calcula la evolución de la distribución de sentimientos.

    Args:
        df: DataFrame con columnas 'fecha' y 'Clasificacion'.
        frequency: Frecuencia de agrupación ('M' mensual, 'Q' trimestral).

    Returns:
        DataFrame con columnas 'fecha', 'Clasificacion', 'cantidad',
        'porcentaje'.
    """
    if frequency == 'M':
        frequency = 'ME'

    if (df.empty or 'fecha' not in df.columns or
            'Clasificacion' not in df.columns):
        return pd.DataFrame()

    df = df.copy()
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    df = df.dropna(subset=['fecha', 'Clasificacion'])

    if df.empty:
        return pd.DataFrame()

    # Agrupar por fecha y clasificación
    dist = df.groupby([
        pd.Grouper(key='fecha', freq=frequency),
        'Clasificacion'
    ]).size().reset_index(name='cantidad')

    if dist.empty:
        return pd.DataFrame()

    # Calcular porcentajes por fecha
    totals = dist.groupby('fecha')['cantidad'].transform('sum')
    dist['porcentaje'] = (dist['cantidad'] / totals) * 100

    return dist


def calculate_trend_change(
    trend_df: pd.DataFrame,
    metric_col: str = 'calificacion'
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """
    Calcula el cambio entre el último y el penúltimo valor de una tendencia.

    Args:
        trend_df: DataFrame de tendencia ordenado por fecha.
        metric_col: Nombre de la columna de métrica.

    Returns:
        Tuple (valor_actual, valor_anterior, delta).
        Retorna (None, None, None) si no hay suficientes datos.
    """
    if len(trend_df) < 2 or metric_col not in trend_df.columns:
        return None, None, None

    last_val = trend_df.iloc[-1][metric_col]
    prev_val = trend_df.iloc[-2][metric_col]
    delta = last_val - prev_val

    return last_val, prev_val, delta
