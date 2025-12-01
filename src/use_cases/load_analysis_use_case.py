import pandas as pd
from use_cases.ports.analysis_repository import IAnalysisRepository
from domain.services.sentiment_mapper import convert_dataframe_classifications


class LoadAnalysisUseCase:
    """
    Este caso de uso recupera un análisis guardado específico por su nombre.
    """

    def __init__(self, analysis_repository: IAnalysisRepository):
        self._analysis_repository = analysis_repository

    def execute(self, analysis_name: str) -> pd.DataFrame:
        """
        Ejecuta el caso de uso.

        Args:
            analysis_name: El nombre del análisis a cargar.

        Returns:
            Un DataFrame que contiene los datos del análisis cargado.
        """
        raw_df = self._analysis_repository.load(analysis_name)
        if raw_df.empty:
            return raw_df
        df = convert_dataframe_classifications(raw_df)
        if 'Fiabilidad' not in df.columns:
            df['Fiabilidad'] = 'N/A'
        return df
