# persistencia_servicio.py
import pandas as pd
import os
from datetime import datetime

class GuardarDatosArchivo:
    """
    Se encarga de la persistencia y almacenamiento de datos en archivos.
    """
    def __init__(self, directorio_base: str = 'datos_procesados'):
        """
        Inicializa el servicio de guardado.

        Args:
            directorio_base (str): La carpeta donde se guardarán los archivos.
        """
        self.directorio_base = directorio_base
        os.makedirs(self.directorio_base, exist_ok=True)
        print(f"Servicio de Guardado inicializado. Los archivos se guardarán en '{self.directorio_base}/'")

    def guardar_datos_limpios(self, datos: pd.DataFrame, nombre_base_archivo: str) -> bool:
        """
        Guarda los datos limpios en formato CSV, usando un nombre de archivo dinámico.

        Args:
            datos (pd.DataFrame): El DataFrame con los datos limpios.
            nombre_base_archivo (str): El nombre base para el archivo de salida
                                       (ej. 'c_Mayo_2025').

        Returns:
            bool: True si se guardó correctamente, False en caso de error.
        """
        if not isinstance(datos, pd.DataFrame) or datos.empty:
            print("Error: No se proporcionaron datos válidos para guardar.")
            return False
            
        # Construir la ruta completa del archivo
        ruta_completa = os.path.join(self.directorio_base, f"{nombre_base_archivo}_limpio.csv")
        
        print(f"Intentando guardar datos en: '{ruta_completa}'")
        try:
            datos.to_csv(ruta_completa, index=False, encoding='utf-8-sig')
            print(f"¡Éxito! Datos guardados correctamente en '{ruta_completa}'.")
            return True
        except Exception as e:
            print(f"ERROR: No se pudo guardar el archivo. Razón: {e}")
            return False

    def crear_respaldo(self, datos: pd.DataFrame, nombre_base_archivo: str) -> bool:
        """
        Crea un respaldo de los datos con un timestamp en el nombre del archivo.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_respaldo = f"{nombre_base_archivo}_respaldo_{timestamp}.csv"
        ruta_respaldo = os.path.join(self.directorio_base, nombre_respaldo)
        
        print(f"Creando respaldo en: '{ruta_respaldo}'")
        return self.guardar_datos_limpios(datos, f"{nombre_base_archivo}_respaldo_{timestamp}")
    
    def validar_integridad_datos(self, ruta_archivo: str) -> bool:
        """
        Valida si un archivo CSV se puede leer correctamente con pandas.
        """
        try:
            pd.read_csv(ruta_archivo)
            print(f"Validación de integridad exitosa para '{ruta_archivo}'.")
            return True
        except Exception as e:
            print(f"Fallo en la validación de integridad para '{ruta_archivo}'. Razón: {e}")
            return False
    
    def obtener_metadatos_archivo(self, ruta_archivo: str) -> dict:
        """
        Obtiene metadatos básicos de un archivo.
        """
        try:
            stat = os.stat(ruta_archivo)
            metadatos = {
                'ruta': ruta_archivo,
                'tamaño_bytes': stat.st_size,
                'ultima_modificacion': datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
            return metadatos
        except FileNotFoundError:
            print(f"No se pudo obtener metadatos. Archivo no encontrado: '{ruta_archivo}'")
            return {}