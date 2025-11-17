from abc import ABC, abstractmethod
import pandas as pd


class IDataCleaner(ABC):
    """
    Puerto (Interfaz) para un servicio que limpia datos de reseñas.
    """

    @abstractmethod
    def clean_data(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """
        Toma un DataFrame sin procesar y devuelve una versión limpia del mismo.

        Args:
            raw_data: DataFrame que contiene al menos las columnas 'comentarios'
            y 'calificacion'.

        Returns:
            Un DataFrame limpio y listo para el análisis.
        """
        pass
