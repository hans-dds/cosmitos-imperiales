"""
Caso de uso para preparar datos de análisis para visualización.

Este caso de uso encapsula la lógica de preparación de datos
antes de mostrarlos en la UI.
"""

import pandas as pd
from typing import Tuple, Dict
from domain.services.metrics_calculator import calculate_comment_length
from infrastructure.ui.constants import get_color_map


class PrepareAnalysisDisplayUseCase:
    """
    Caso de uso para preparar datos de análisis para visualización.
    """
    def execute(
            self,
            df: pd.DataFrame) -> Tuple[pd.DataFrame,
                                       Dict[str,
                                            str]]:
        """
        Prepara un DataFrame para visualización agregando columnas
        necesarias y retornando el mapa de colores.
        Args:
            df: DataFrame con los datos del análisis
        Returns:
            Tupla con (DataFrame preparado, mapa de colores)
        """
        # Calcular longitud de comentarios si no existe
        df_prepared = calculate_comment_length(df)
        # Obtener mapa de colores
        color_map = get_color_map()
        return df_prepared, color_map
