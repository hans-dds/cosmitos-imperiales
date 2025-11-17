from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd


class IFileReader(ABC):
    """
    Puerto (Interfaz) para un servicio que lee archivos CSV y Excel.
    """

    @abstractmethod
    def read_file(self, file_object, file_type: str) -> pd.DataFrame:
        """
        Lee un archivo y lo convierte en un DataFrame.

        Args:
            file_object: El objeto de archivo cargado (desde Streamlit u otra fuente).
            file_type: El tipo MIME del archivo (ej., "text/csv" o 
                      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet").

        Returns:
            Un DataFrame con los datos del archivo.

        Raises:
            ValueError: Si el tipo de archivo no es soportado o hay un error al leerlo.
        """
        pass

