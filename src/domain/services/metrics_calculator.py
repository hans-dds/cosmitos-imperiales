"""
Servicio de dominio para calcular métricas de análisis.

Este módulo encapsula la lógica de cálculo de métricas relacionadas
con los análisis de sentimientos, manteniendo esta lógica en el dominio.
"""

import pandas as pd
from typing import Dict


def calculate_comment_length(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula la longitud de los comentarios en un DataFrame.
    
    Args:
        df: DataFrame con la columna 'comentarios'
        
    Returns:
        DataFrame con una columna adicional 'longitud'
    """
    if 'comentarios' not in df.columns:
        return df
    
    df = df.copy()
    if 'longitud' not in df.columns:
        df['longitud'] = df['comentarios'].str.len()
    
    return df


def calculate_summary_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula métricas de resumen agrupadas por clasificación.
    
    Args:
        df: DataFrame con las columnas 'Clasificacion', 'comentarios' y opcionalmente 'longitud'
        
    Returns:
        DataFrame con el resumen por clasificación con columnas:
        - Clasificacion
        - NumComentarios
        - LongitudPromedio
        - Porcentaje
    """
    if df.empty or 'Clasificacion' not in df.columns:
        return pd.DataFrame()
    
    # Asegurar que existe la columna 'longitud' para el cálculo
    df = calculate_comment_length(df)
    
    # Crear el resumen con las columnas necesarias en el orden correcto
    summary = df.groupby('Clasificacion').agg(
        NumComentarios=('comentarios', 'count'),
        LongitudPromedio=('longitud', 'mean') if 'longitud' in df.columns else ('comentarios', lambda x: x.str.len().mean()),
        Porcentaje=('comentarios', lambda x: (len(x) / len(df)) * 100)
    ).reset_index()
    
    # Asegurar el orden correcto de las columnas
    summary = summary[['Clasificacion', 'NumComentarios', 'LongitudPromedio', 'Porcentaje']]
    
    # Redondear valores numéricos
    if 'LongitudPromedio' in summary.columns:
        summary['LongitudPromedio'] = summary['LongitudPromedio'].round(2)
    if 'Porcentaje' in summary.columns:
        summary['Porcentaje'] = summary['Porcentaje'].round(2)
    
    return summary



