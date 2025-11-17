import pandas as pd
from use_cases.ports.file_reader import IFileReader


class ReadFileUseCase:
    """
    Este caso de uso lee un archivo CSV o Excel y lo convierte en un DataFrame.
    """

    def __init__(self, file_reader: IFileReader):
        self._file_reader = file_reader

    def execute(self, file_object, file_type: str) -> pd.DataFrame:
        """
        Ejecuta el caso de uso.

        Args:
            file_object: El objeto de archivo cargado (desde Streamlit).
            file_type: El tipo MIME del archivo.

        Returns:
            Un DataFrame con los datos del archivo.

        Raises:
            ValueError: Si el tipo de archivo no es soportado o hay un error al leerlo.
        """
        return self._file_reader.read_file(file_object, file_type)

