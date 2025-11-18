"""
Servicio de dominio para calcular la fiabilidad de las predicciones de
sentimiento.

Este módulo encapsula la lógica de negocio para determinar la fiabilidad
de una predicción de sentimiento basada en probabilidades del modelo
o en la calificación proporcionada.
"""

import pandas as pd
from typing import Union


def calculate_reliability_from_probability(probability: float) -> float:
    """
    Calcula la fiabilidad basada en la probabilidad máxima del modelo.
    La fiabilidad es simplemente la probabilidad máxima de la predicción,
    que indica qué tan seguro está el modelo de su clasificación.
    Args:
        probability: Probabilidad máxima de la predicción (0.0 a 1.0)
    Returns:
        Fiabilidad como valor numérico (0.0 a 1.0)
    """
    return float(probability)


def calculate_reliability_from_rating(rating: Union[int, float]) -> str:
    """
    Calcula la fiabilidad basada en la calificación cuando el modelo
    no proporciona probabilidades.
    Reglas de negocio:
    - Alta: calificación <= 2 o >= 9 (extremadamente negativa o positiva)
    - Media: calificación <= 4 o >= 7 (moderadamente negativa o positiva)
    - Baja: calificación entre 5 y 6 (neutra, ambigua)
    Args:
        rating: Calificación numérica (típicamente 1-10)
    Returns:
        Fiabilidad como categoría: "Alta", "Media", o "Baja"
    """
    try:
        rating_float = float(rating)
        if rating_float <= 2 or rating_float >= 9:
            return "Alta"
        elif rating_float <= 4 or rating_float >= 7:
            return "Media"
        else:
            return "Baja"
    except (ValueError, TypeError):
        return "N/A"


def add_reliability_column(
    df: pd.DataFrame,
    probabilities: pd.Series = None,
    use_rating_fallback: bool = True
) -> pd.DataFrame:
    """
    Agrega una columna de fiabilidad al DataFrame.
    Si se proporcionan probabilidades, usa esas. Si no, y
    use_rating_fallback es True, usa la calificación como fallback.
    Args:
        df: DataFrame con los datos
        probabilities: Serie con probabilidades máximas (opcional)
        use_rating_fallback: Si True, usa calificación cuando no hay
        probabilidades
    Returns:
        DataFrame con la columna 'Fiabilidad' agregada
    """
    df = df.copy()
    if probabilities is not None and len(probabilities) == len(df):
        # Usar probabilidades del modelo
        df['Fiabilidad'] = probabilities.apply(
            calculate_reliability_from_probability)
    elif use_rating_fallback and 'calificacion' in df.columns:
        # Usar calificación como fallback
        df['Fiabilidad'] = df['calificacion'].apply(
            calculate_reliability_from_rating)
    else:
        # Valor por defecto
        df['Fiabilidad'] = 'N/A'
    return df
