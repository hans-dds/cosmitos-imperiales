from abc import ABC, abstractmethod
import pandas as pd


class ISentimentAnalyzer(ABC):
    """
    Port (Interface) for a service that performs sentiment
    analysis on review data.
    """

    @abstractmethod
    def analyze(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Takes a DataFrame with cleaned reviews and returns
        it with sentiment predictions.

        Args:
            data: DataFrame containing at least 'comentarios'
            and 'calificacion' columns.

        Returns:
            A DataFrame with an added 'Clasificacion' column
            containing sentiment predictions.
        """
        pass
