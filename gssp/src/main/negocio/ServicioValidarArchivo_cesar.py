import os
import pandas as pd
from typing import Tuple, Optional


class ServicioValidarArchivo:
    """
    Se encarga de leer el archivo de Excel y preparar los datos para su almacenamiento.
    """
    
    def __init__(self):
        self.extensiones_validas = ['.xlsx', '.xls']
        self._ruta_archivo = None
        self._nombre_archivo = None
        self._datos_archivo = None
    
    def leer_archivo(self, ruta_archivo: str) -> Tuple[bool, Optional[str], Optional[pd.DataFrame]]:
        """
        Orquesta la validación y lectura del archivo.
        
        Args:
            ruta_archivo (str): La ruta completa del archivo a validar
            
        Returns:
            Tuple[bool, Optional[str], Optional[pd.DataFrame]]: 
                - bool: True si el archivo es válido, False en caso contrario
                - str: Mensaje de error si la validación falla, None si es exitosa
                - pd.DataFrame: Los datos del archivo si es válido, None en caso contrario
        """
        try:
            # Validar formato del archivo
            es_valido, mensaje_error = self.validar_formato_archivo(ruta_archivo)
            if not es_valido:
                return False, mensaje_error, None
            
            # Si el formato es válido, intentar leer el archivo
            datos = self._leer_datos_excel(ruta_archivo)
            if datos is not None:
                return True, None, datos
            else:
                return False, "Error al leer el contenido del archivo Excel.", None
                
        except Exception as e:
            return False, f"Error inesperado al procesar el archivo: {str(e)}", None
    
    def obtener_ruta_archivo(self) -> Optional[str]:
        """
        Obtiene la ruta del archivo validado.
        
        Returns:
            Optional[str]: La ruta completa del archivo o None si no hay archivo válido
        """
        return self._ruta_archivo
        
    def obtener_nombre_archivo(self) -> Optional[str]:
        """
        Obtiene el nombre del archivo validado.
        
        Returns:
            Optional[str]: El nombre del archivo o None si no hay archivo válido
        """
        return self._nombre_archivo
        
    def obtener_datos_archivo(self) -> Optional[pd.DataFrame]:
        """
        Obtiene los datos del archivo validado.
        
        Returns:
            Optional[pd.DataFrame]: Los datos del archivo o None si no hay archivo válido
        """
        return self._datos_archivo
    
    def hay_archivo_valido(self) -> bool:
        """
        Verifica si hay un archivo válido cargado.
        
        Returns:
            bool: True si hay un archivo válido, False en caso contrario
        """
        return (self._ruta_archivo is not None and 
                self._nombre_archivo is not None and 
                self._datos_archivo is not None)
    
    def _limpiar_estado(self):
        """Limpia el estado interno del servicio."""
        self._ruta_archivo = None
        self._nombre_archivo = None
        self._datos_archivo = None

    def validar_formato_archivo(self, ruta_archivo: str) -> Tuple[bool, Optional[str]]:
        """
        Verifica que el Excel tiene el formato correcto.
        
        Args:
            ruta_archivo (str): La ruta completa del archivo a validar
            
        Returns:
            Tuple[bool, Optional[str]]: 
                - bool: True si el archivo es válido, False en caso contrario
                - str: Mensaje de error si la validación falla, None si es exitosa
        """
        # Validar que el archivo existe
        if not os.path.exists(ruta_archivo):
            return False, "El archivo seleccionado no existe."
            
        # Validar que es un archivo (no un directorio)
        if not os.path.isfile(ruta_archivo):
            return False, "La ruta seleccionada no es un archivo válido."
            
        # Validar extensión del archivo
        extension = os.path.splitext(ruta_archivo)[1].lower()
        if extension not in self.extensiones_validas:
            return False, "Por favor, selecciona un archivo Excel válido (.xlsx o .xls)."
        
        # Leer los datos del Excel
        datos = self._leer_datos_excel(ruta_archivo)
        if datos is None:
            return False, "No se pudo leer el contenido del archivo Excel."
        
        # Validar que es un diccionario (múltiples hojas)
        if not isinstance(datos, dict):
            return False, "El archivo Excel debe contener exactamente dos hojas."
        
        # Validar que tiene exactamente 2 hojas
        if len(datos) != 2:
            return False, f"El archivo Excel debe tener exactamente 2 hojas, pero tiene {len(datos)}."
        
        # Obtener los nombres de las hojas
        nombres_hojas = list(datos.keys())
        
        # Validar nombres específicos de las hojas
        if 'ATC' not in nombres_hojas:
            return False, "El archivo Excel debe contener una hoja llamada 'ATC'."
        
        if 'Encuesta salida' not in nombres_hojas:
            return False, "El archivo Excel debe contener una hoja llamada 'Encuesta salida'."
        
        # Validar columnas en cada hoja
        columnas_requeridas = ['Calificacion', 'Comentarios']
        
        # Validar hoja ATC
        df_atc = datos['ATC']
        for columna in columnas_requeridas:
            if columna not in df_atc.columns:
                return False, f"La hoja 'ATC' debe contener la columna '{columna}'."
        
        # Validar hoja Encuesta salida
        df_encuesta = datos['Encuesta salida']
        for columna in columnas_requeridas:
            if columna not in df_encuesta.columns:
                return False, f"La hoja 'Encuesta salida' debe contener la columna '{columna}'."
        
        return True, "Excel válido y con formato correcto"
        
            
       
    def _leer_datos_excel(self, ruta_archivo: str) -> Optional[pd.DataFrame]:
        """
        Lee los datos del archivo Excel.
        
        Args:
            ruta_archivo (str): La ruta completa del archivo Excel
            
        Returns:
            Optional[pd.DataFrame]: Los datos del archivo o None si hay error
        """
        try:
            # Intentar leer el archivo Excel
            excel_file = pd.ExcelFile(ruta_archivo)
            nombres_hojas = excel_file.sheet_names
            
            print(f"Hojas encontradas: {nombres_hojas}")
            print(f"Número de hojas: {len(nombres_hojas)}")
            
            if len(nombres_hojas) > 1:
                
                datos_todas_hojas = pd.read_excel(ruta_archivo, sheet_name=None)
            
                
                for nombre_hoja, df in datos_todas_hojas.items():
                    print(f"Hoja '{nombre_hoja}': {df.shape[0]} filas, {df.shape[1]} columnas, nombres de columnas: {df.columns.tolist()}")
                
                # Retornar el diccionario con todas las hojas
                return datos_todas_hojas
            else:
                datos = pd.read_excel(ruta_archivo)
                return datos
        except Exception as e:
            print(f"Error al leer el archivo Excel: {str(e)}")
            return None
   
            
       