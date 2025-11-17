import pandas as pd
from typing import List

from use_cases.ports.file_reader import IFileReader


class PandasFileReader(IFileReader):
    """
    Una implementación concreta de IFileReader que utiliza pandas
    para leer archivos CSV y Excel.
    """

    def __init__(self, required_sheets: List[str] = None):
        """
        Inicializa el lector de archivos.

        Args:
            required_sheets: Lista de nombres de hojas requeridas para archivos Excel.
                            Si es None, usa las hojas por defecto ["ATC", "Encuesta salida"].
        """
        self._required_sheets = required_sheets or ["ATC", "Encuesta salida"]

    def read_file(self, file_object, file_type: str) -> pd.DataFrame:
        """
        Lee un archivo CSV o Excel y lo convierte en un DataFrame.

        Args:
            file_object: El objeto de archivo cargado (desde Streamlit).
            file_type: El tipo MIME del archivo.

        Returns:
            Un DataFrame con los datos del archivo.

        Raises:
            ValueError: Si el tipo de archivo no es soportado o hay un error al leerlo.
        """
        if file_type == "text/csv":
            return self._read_csv(file_object)
        elif file_type in [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel"
        ]:
            return self._read_excel(file_object)
        else:
            raise ValueError(f"Tipo de archivo no soportado: {file_type}")

    def _read_csv(self, file_object) -> pd.DataFrame:
        """Lee un archivo CSV."""
        try:
            return pd.read_csv(file_object)
        except Exception as e:
            raise ValueError(f"Error al leer el archivo CSV: {e}")

    def _read_excel(self, file_object) -> pd.DataFrame:
        """
        Lee un archivo Excel y combina las hojas requeridas en un solo DataFrame.
        """
        try:
            # Leer todas las hojas del archivo Excel
            raw_df_dict = pd.read_excel(file_object, sheet_name=None)
            
            # Filtrar solo las hojas requeridas
            df_list = [
                df_sheet for sheet_name, df_sheet in raw_df_dict.items()
                if sheet_name in self._required_sheets
            ]
            
            if not df_list:
                raise ValueError(
                    f"No se encontraron las hojas requeridas: {self._required_sheets}")
            
            # Concatenar todas las hojas en un solo DataFrame
            return pd.concat(df_list, ignore_index=True)
        except Exception as e:
            raise ValueError(f"Error al leer el archivo Excel: {e}")

