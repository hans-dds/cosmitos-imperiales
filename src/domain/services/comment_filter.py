"""
Servicio de dominio para filtrar comentarios irrelevantes.

Este módulo encapsula las reglas de negocio sobre qué comentarios
se consideran irrelevantes y deben ser filtrados.
"""

import pandas as pd
from typing import List


def get_irrelevant_patterns() -> List[str]:
    """
    Retorna los patrones de comentarios que se consideran irrelevantes.
    
    Estos patrones representan reglas de negocio sobre qué comentarios
    no proporcionan retroalimentación significativa.
    
    Returns:
        Lista de patrones regex para filtrar comentarios irrelevantes
    """
    return [
        r'^solo califica',
        r'^no (?:brinda|proporciona|quiso|tiene|contesta)',
        r'^sin comentarios?$',
        r'^ningun[ao]s?$',
        r'^\d+cm$',
        r'^se envia whatsapp$',
        r'^(?:bdc|ok|na|s c)$'
    ]


def filter_irrelevant_comments(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filtra los comentarios que no proporcionan retroalimentación significativa.
    
    Args:
        df: DataFrame con la columna 'comentarios'
        
    Returns:
        DataFrame filtrado sin comentarios irrelevantes
    """
    if 'comentarios' not in df.columns:
        return df
    
    patterns = get_irrelevant_patterns()
    regex_filter = '|'.join(patterns)
    
    irrelevant_mask = df['comentarios'].str.contains(
        regex_filter,
        regex=True,
        na=False
    )
    short_mask = df['comentarios'].str.len() < 5
    
    return df[~(irrelevant_mask | short_mask)]

