from typing import List
from use_cases.ports.analysis_repository import IAnalysisRepository


class ListAnalysesUseCase:
    """
    Este caso de uso recupera la lista de todos los análisis guardados previamente.
    """

    def __init__(self, analysis_repository: IAnalysisRepository):
        self._analysis_repository = analysis_repository

    def execute(self) -> List[str]:
        """
        Ejecuta el caso de uso.

        Returns:
            Una lista de nombres de los análisis guardados.
        """
        return self._analysis_repository.list_analyses()
