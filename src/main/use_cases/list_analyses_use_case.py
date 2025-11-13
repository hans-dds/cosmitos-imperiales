from typing import List
from use_cases.ports.analysis_repository import IAnalysisRepository


class ListAnalysesUseCase:
    """
    This use case retrieves the list of all previously saved analyses.
    """

    def __init__(self, analysis_repository: IAnalysisRepository):
        self._analysis_repository = analysis_repository

    def execute(self) -> List[str]:
        """
        Executes the use case.

        Returns:
            A list of names of the saved analyses.
        """
        return self._analysis_repository.list_analyses()
