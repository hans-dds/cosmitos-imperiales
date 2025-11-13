import pandas as pd

from use_cases.ports.data_cleaner import IDataCleaner
from use_cases.ports.sentiment_analyzer import ISentimentAnalyzer
from use_cases.ports.analysis_repository import IAnalysisRepository


class ProcessFileUseCase:
    """
    This use case orchestrates the cleaning, analysis, and storage of review
    data from a file.
    """

    def __init__(
        self,
        data_cleaner: IDataCleaner,
        sentiment_analyzer: ISentimentAnalyzer,
        analysis_repository: IAnalysisRepository,
    ):
        self._data_cleaner = data_cleaner
        self._sentiment_analyzer = sentiment_analyzer
        self._analysis_repository = analysis_repository

    def execute(
            self,
            raw_data: pd.DataFrame,
            file_basename: str) -> pd.DataFrame:
        """
        Executes the use case.

        Args:
            raw_data: The raw DataFrame read from the uploaded file.
            file_basename: The base name of the original file
            (e.g., 'c_Abril_2025').

        Returns:
            The DataFrame containing the analyzed data.
        """
        # 1. Clean the data
        cleaned_data = self._data_cleaner.clean_data(raw_data)
        if cleaned_data.empty:
            raise ValueError("Data is empty after cleaning process.")

        # 2. Analyze sentiment
        analyzed_data = self._sentiment_analyzer.analyze(cleaned_data)
        if analyzed_data.empty:
            raise ValueError("Data is empty after sentiment analysis.")

        # 3. Save the results
        table_name = f"analisis_{file_basename}"
        self._analysis_repository.save_csv(analyzed_data, file_basename)
        self._analysis_repository.save_mysql(analyzed_data, table_name)

        return analyzed_data
