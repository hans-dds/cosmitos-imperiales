import pandas as pd
from use_cases.ports.analysis_repository import IAnalysisRepository


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
        return self._analysis_repository.load_analysis(analysis_name)
