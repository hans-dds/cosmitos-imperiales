import pandas as pd
from typing import Tuple, Optional, Union
from io import BytesIO

class ServicioValidarArchivo:
    """
    Valida y carga archivos Excel directamente desde objetos en memoria.
    """

    def __init__(self):
        self.extensiones_validas = ['.xlsx', '.xls']
        self._datos_archivo = None

    def leer_archivo(self, file: BytesIO, nombre_archivo: str) -> Tuple[bool, Optional[str]]:
        """
        Valida y lee un archivo Excel recibido como stream en memoria.

        Args:
            file (BytesIO): Archivo cargado desde Streamlit.
            nombre_archivo (str): Nombre del archivo (para validar la extensión).

        Returns:
            Tuple[bool, Optional[str]]: 
                - bool: True si el archivo es válido
                - str: mensaje de error (si falla)
        """
        extension = nombre_archivo.split('.')[-1].lower()
        if f'.{extension}' not in self.extensiones_validas:
            return False, "Extensión inválida. Solo se permiten archivos .xlsx o .xls"

        try:
            datos = self._leer_datos_excel(file, extension)
            if datos is None:
                return False, "No se pudo leer el contenido del archivo Excel."

            validado, mensaje = self._validar_estructura(datos)
            if not validado:
                return False, mensaje

            self._datos_archivo = datos
            return True, None

        except Exception as e:
            return False, f"Error inesperado al procesar el archivo: {str(e)}"

    def _leer_datos_excel(self, archivo_stream: BytesIO, extension: str) -> Optional[Union[pd.DataFrame, dict]]:
        try:
            archivo_stream.seek(0)  # importante reiniciar el stream antes de leer
            if extension == 'xlsx':
                # Usa openpyxl para .xlsx
                datos = pd.read_excel(archivo_stream, sheet_name=None, engine='openpyxl')
            elif extension == 'xls':
                # Usa xlrd para .xls
                datos = pd.read_excel(archivo_stream, sheet_name=None, engine='xlrd')
            else:
                return None

            return datos

        except Exception as e:
            print(f"Error al leer el archivo Excel: {str(e)}")
            return None

    def _validar_estructura(self, datos: Union[pd.DataFrame, dict]) -> Tuple[bool, Optional[str]]:
        if not isinstance(datos, dict):
            return False, "El archivo Excel debe contener exactamente dos hojas."

        if len(datos) != 2:
            return False, f"El archivo Excel debe tener exactamente 2 hojas, pero tiene {len(datos)}."

        nombres_hojas = list(datos.keys())

        if 'ATC' not in nombres_hojas:
            return False, "El archivo Excel debe contener una hoja llamada 'ATC'."

        if 'Encuesta salida' not in nombres_hojas:
            return False, "El archivo Excel debe contener una hoja llamada 'Encuesta salida'."

        columnas_requeridas = ['Calificacion', 'Comentarios']

        for hoja, df in datos.items():
            for col in columnas_requeridas:
                if col not in df.columns:
                    return False, f"La hoja '{hoja}' debe contener la columna '{col}'."

        return True, None

    def obtener_datos_archivo(self) -> Optional[Union[pd.DataFrame, dict]]:
        return self._datos_archivo
