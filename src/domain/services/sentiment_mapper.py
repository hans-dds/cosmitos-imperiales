"""Servicio de mapeo de sentimientos.

Responsabilidad: convertir representaciones numéricas de sentimiento a
value objects/texto de dominio. Vive en la capa de dominio para que tanto
casos de uso como adaptadores (si fuera estrictamente necesario) puedan
reutilizarlo sin invertir la dirección de dependencias.
"""

import pandas as pd
from domain.value_objects.sentiment import Sentiment


def convert_numeric_to_sentiment(value) -> str:
    """Convierte un valor numérico (-1, 0, 1) en su clasificación textual.

    Si el valor ya es texto o no se puede convertir, se retorna tal cual.
    """
    try:
        if pd.notna(value):
            numeric_val = int(float(value))
            return Sentiment.from_numeric(numeric_val).value
        return value
    except (ValueError, TypeError):
        return value


def convert_dataframe_classifications(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte la columna 'Clasificacion' a texto si contiene valores numéricos.
    """
    if df.empty or 'Clasificacion' not in df.columns:
        return df
    df = df.copy()
    if df['Clasificacion'].dtype in ['int64', 'float64']:
        df['Clasificacion'] = df['Clasificacion'].apply(convert_numeric_to_sentiment)
    elif df['Clasificacion'].dtype == 'object':
        numeric_mask = pd.to_numeric(df['Clasificacion'], errors='coerce').notna()
        if numeric_mask.any():
            df.loc[numeric_mask, 'Clasificacion'] = df.loc[numeric_mask, 'Clasificacion'].apply(convert_numeric_to_sentiment)
    return df
