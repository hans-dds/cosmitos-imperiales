from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Tuple


class IAnalysisRepository(ABC):
    """
    Port (Interface) for a repository that handles persistence of analysis results.
    """

    @abstractmethod
    def save_csv(self, data: pd.DataFrame, file_name: str) -> Tuple[bool, str]:
        """
        Saves the analysis data to a CSV file.

        Args:
            data: The DataFrame to save.
            file_name: The base name for the output file.

        Returns:
            A tuple containing a success flag and a message.
        """
        pass

    @abstractmethod
    def save_mysql(self, data: pd.DataFrame, table_name: str) -> Tuple[bool, str]:
        """
        Saves the analysis data to a MySQL table.

        Args:
            data: The DataFrame to save.
            table_name: The name of the table to save the data into.

        Returns:
            A tuple containing a success flag and a message.
        """
        pass

    @abstractmethod
    def list_analyses(self) -> List[str]:
        """
        Lists the names of previously saved analyses (e.g., tables in the DB).

        Returns:
            A list of analysis names.
        """
        pass

    @abstractmethod
    def load_analysis(self, name: str) -> pd.DataFrame:
        """
        Loads a specific analysis by its name.

        Args:
            name: The name of the analysis to load.

        Returns:
            A DataFrame containing the analysis data.
        """
        pass
