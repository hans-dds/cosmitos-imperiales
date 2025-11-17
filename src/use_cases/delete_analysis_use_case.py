from typing import Tuple, List
from use_cases.ports.analysis_repository import IAnalysisRepository


class DeleteAnalysisUseCase:
    """
    Este caso de uso elimina uno o múltiples análisis guardados.
    """

    def __init__(self, analysis_repository: IAnalysisRepository):
        self._analysis_repository = analysis_repository

    def execute(self, analysis_name: str) -> Tuple[bool, str]:
        """
        Ejecuta el caso de uso para eliminar un solo análisis.

        Args:
            analysis_name: El nombre del análisis a eliminar.

        Returns:
            Una tupla que contiene un indicador de éxito y un mensaje.
        """
        return self._analysis_repository.delete_analysis(analysis_name)

    def execute_multiple(self, analysis_names: List[str]) -> Tuple[bool, List[Tuple[str, bool, str]]]:
        """
        Ejecuta el caso de uso para eliminar múltiples análisis.

        Args:
            analysis_names: Lista de nombres de análisis a eliminar.

        Returns:
            Una tupla que contiene un indicador de éxito general y una lista de
            resultados individuales (nombre, éxito, mensaje).
        """
        return self._analysis_repository.delete_multiple_analyses(analysis_names)

