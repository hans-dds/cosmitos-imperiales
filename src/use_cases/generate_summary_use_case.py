"""
Caso de uso para generar resumen de análisis.

Este caso de uso encapsula la lógica de generación de resúmenes
de análisis de sentimientos.
"""

import pandas as pd
from domain.services.metrics_calculator import calculate_summary_metrics


class GenerateSummaryUseCase:
    """
    Caso de uso para generar un resumen de análisis.
    """
    
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Genera un DataFrame de resumen agrupado por clasificación.
        
        Args:
            df: DataFrame con las columnas 'Clasificacion', 'comentarios' y opcionalmente 'longitud'
            
        Returns:
            DataFrame con el resumen por clasificación
        """
        return calculate_summary_metrics(df)

