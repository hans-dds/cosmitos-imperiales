from abc import ABC, abstractmethod
import pandas as pd


class IDataCleaner(ABC):
    """
    Port (Interface) for a service that cleans review data.
    """

    @abstractmethod
    def clean_data(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """
        Takes a raw DataFrame and returns a cleaned version of it.

        Args:
            raw_data: DataFrame containing at least 'comentarios'
            and 'calificacion' columns.

        Returns:
            A cleaned DataFrame ready for analysis.
        """
        pass
