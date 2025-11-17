"""
Mapper para convertir valores numéricos de clasificación a objetos Sentiment.

Este módulo encapsula la lógica de conversión entre representaciones numéricas
y de dominio de los sentimientos. Está en la capa de casos de uso porque
trabaja con pandas (representación técnica) y lo convierte a dominio.
"""

import pandas as pd
from domain.value_objects.sentiment import Sentiment


def convert_numeric_to_sentiment(value) -> str:
    """
    Convierte un valor numérico a su representación de sentimiento en texto.
    
    Args:
        value: Valor numérico (-1, 0, o 1) o valor ya en texto
        
    Returns:
        String con la clasificación ("Detractor", "Neutro", o "Promotor")
        
    Raises:
        ValueError: Si el valor no es válido
    """
    try:
        if pd.notna(value):
            numeric_val = int(float(value))
            return Sentiment.from_numeric(numeric_val).value
        return value
    except (ValueError, TypeError):
        # Si ya es texto o no se puede convertir, retornar tal cual
        return value


def convert_dataframe_classifications(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convierte las clasificaciones numéricas en un DataFrame a texto.
    
    Args:
        df: DataFrame que puede contener clasificaciones numéricas en la columna 'Clasificacion'
        
    Returns:
        DataFrame con las clasificaciones convertidas a texto
    """
    if df.empty or 'Clasificacion' not in df.columns:
        return df
    
    df = df.copy()
    
    # Solo convertir si los valores son numéricos
    if df['Clasificacion'].dtype in ['int64', 'float64']:
        df['Clasificacion'] = df['Clasificacion'].apply(convert_numeric_to_sentiment)
    elif df['Clasificacion'].dtype == 'object':
        # Verificar si hay valores numéricos mezclados con texto
        numeric_mask = pd.to_numeric(df['Clasificacion'], errors='coerce').notna()
        if numeric_mask.any():
            df.loc[numeric_mask, 'Clasificacion'] = df.loc[numeric_mask, 'Clasificacion'].apply(
                convert_numeric_to_sentiment
            )
    
    return df

