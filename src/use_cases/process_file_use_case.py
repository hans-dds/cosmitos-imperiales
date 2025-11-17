import pandas as pd

from use_cases.ports.data_cleaner import IDataCleaner
from use_cases.ports.sentiment_analyzer import ISentimentAnalyzer
from use_cases.ports.analysis_repository import IAnalysisRepository


class ProcessFileUseCase:
    """
    Este caso de uso orquesta la limpieza, análisis y almacenamiento de datos
    de reseñas desde un archivo.
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
        Ejecuta el caso de uso.

        Args:
            raw_data: El DataFrame sin procesar leído del archivo subido.
            file_basename: El nombre base del archivo original
            (ej., 'c_Abril_2025').

        Returns:
            El DataFrame que contiene los datos analizados.
        """
        # 1. Limpiar los datos
        cleaned_data = self._data_cleaner.clean_data(raw_data)
        if cleaned_data.empty:
            raise ValueError("Los datos están vacíos después del proceso de limpieza.")

        # 2. Analizar sentimiento
        analyzed_data = self._sentiment_analyzer.analyze(cleaned_data)
        if analyzed_data.empty:
            raise ValueError("Los datos están vacíos después del análisis de sentimiento.")

        # 3. Guardar los resultados
        table_name = f"analisis_{file_basename}"
        self._analysis_repository.save_csv(analyzed_data, file_basename)
        self._analysis_repository.save_mysql(analyzed_data, table_name)

        return analyzed_data
