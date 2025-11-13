import pandas as pd
from use_cases.ports.analysis_repository import IAnalysisRepository


class LoadAnalysisUseCase:
    """
    This use case retrieves a specific saved analysis by its name.
    """

    def __init__(self, analysis_repository: IAnalysisRepository):
        self._analysis_repository = analysis_repository

    def execute(self, analysis_name: str) -> pd.DataFrame:
        """
        Executes the use case.

        Args:
            analysis_name: The name of the analysis to load.

        Returns:
            A DataFrame containing the loaded analysis data.
        """
        return self._analysis_repository.load_analysis(analysis_name)
