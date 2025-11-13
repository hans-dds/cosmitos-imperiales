from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Tuple


class IAnalysisRepository(ABC):
    """
    Puerto (Interfaz) para un repositorio que maneja la persistencia
    de los resultados del análisis.
    """

    @abstractmethod
    def save_csv(self, data: pd.DataFrame, file_name: str) -> Tuple[bool, str]:
        """
        Guarda los datos del análisis en un archivo CSV.

        Args:
            data: El DataFrame a guardar.
            file_name: El nombre base para el archivo de salida.

        Returns:
            Una tupla que contiene un indicador de éxito y un mensaje.
        """
        pass

    @abstractmethod
    def save_mysql(self,
                   data: pd.DataFrame,
                   table_name: str) -> Tuple[bool, str]:
        """
        Guarda los datos del análisis en una tabla de MySQL.

        Args:
            data: El DataFrame a guardar.
            table_name: El nombre de la tabla donde se guardarán los datos.

        Returns:
            Una tupla que contiene un indicador de éxito y un mensaje.
        """
        pass

    @abstractmethod
    def list_analyses(self) -> List[str]:
        """
        Lista los nombres de los análisis guardados previamente (ej. tablas en la BD).

        Returns:
            Una lista de nombres de análisis.
        """
        pass

    @abstractmethod
    def load_analysis(self, name: str) -> pd.DataFrame:
        """
        Carga un análisis específico por su nombre.

        Args:
            name: El nombre del análisis a cargar.

        Returns:
            Un DataFrame que contiene los datos del análisis.
        """
        pass
