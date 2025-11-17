from abc import ABC, abstractmethod
import pandas as pd


class ISentimentAnalyzer(ABC):
    """
    Puerto (Interfaz) para un servicio que realiza análisis de
    sentimientos en datos de reseñas.
    """

    @abstractmethod
    def analyze(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Toma un DataFrame con reseñas limpias y lo devuelve con
        predicciones de sentimiento.

        Args:
            data: DataFrame que contiene al menos las columnas 'comentarios'
            y 'calificacion'.

        Returns:
            Un DataFrame con una columna añadida 'Clasificacion'
            que contiene las predicciones de sentimiento.
        """
        pass
