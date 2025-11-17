import os
from typing import List, Tuple

import mysql.connector
import pandas as pd
from mysql.connector import Error

from use_cases.ports.analysis_repository import IAnalysisRepository


class SQLandCSVAnalysisRepository(IAnalysisRepository):
    """
    Una implementación concreta de IAnalysisRepository que guarda datos en
    archivos MySQL y CSV.
    """

    def __init__(
            self,
            db_config:
            dict,
            csv_base_dir: str = 'datos_analizados'
            ):
        self._db_config = db_config
        self._csv_base_dir = csv_base_dir
        os.makedirs(self._csv_base_dir, exist_ok=True)

    def save_csv(self, data: pd.DataFrame, file_name: str) -> Tuple[bool, str]:
        """Guarda los datos del análisis en un archivo CSV."""
        if data.empty:
            return False, "No se proporcionaron datos para guardar."

        file_path = os.path.join(self._csv_base_dir, f"{file_name}_limpio.csv")
        try:
            data.to_csv(file_path, index=False, encoding='utf-8-sig')
            msg = f"Datos guardados exitosamente en '{file_path}'."
            return True, msg
        except Exception as e:
            return False, f"Fallo al guardar el archivo CSV. Razón: {e}"

    def save_mysql(
            self,
            data: pd.DataFrame,
            table_name: str) -> Tuple[bool, str]:
        """Guarda los datos del análisis en una tabla de MySQL."""
        try:
            with mysql.connector.connect(**self._db_config) as conn:
                with conn.cursor() as cursor:
                    # Esta es una creación de esquema simplificada
                    cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        comentarios TEXT,
                        calificacion FLOAT,
                        Clasificacion VARCHAR(255)
                    )""")

                    for _, row in data.iterrows():
                        sql = (f"INSERT INTO {table_name} "
                               f"(comentarios, calificacion, Clasificacion) "
                               "VALUES (%s, %s, %s)")
                        val = (row['comentarios'], row['calificacion'],
                               row['Clasificacion'])
                        cursor.execute(sql, val)
                    conn.commit()
            msg = f"Datos guardados exitosamente en la tabla MySQL '{table_name}'."
            return True, msg
        except Error as e:
            return False, f"Error al conectar o guardar en MySQL: {e}"

    def list_analyses(self) -> List[str]:
        """Lista las tablas de análisis guardadas de la base de datos."""
        try:
            with mysql.connector.connect(**self._db_config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SHOW TABLES LIKE 'analisis_%'")
                    return [row[0] for row in cursor.fetchall()]
        except Error as e:
            print(f"Error al listar las tablas de análisis: {e}")
            return []

    def load_analysis(self, name: str) -> pd.DataFrame:
        """
        Carga un análisis específico de una tabla de MySQL.
        Convierte valores numéricos de clasificación a texto si es necesario.
        """
        try:
            with mysql.connector.connect(**self._db_config) as conn:
                query = (f"SELECT comentarios, calificacion, Clasificacion "
                         f"FROM {name}")
                df = pd.read_sql(query, conn)
                
                # Si la clasificación está en formato numérico, convertir a texto
                if not df.empty and 'Clasificacion' in df.columns:
                    from domain.value_objects.sentiment import Sentiment
                    
                    # Intentar convertir valores numéricos a texto
                    def convert_classification(value):
                        try:
                            # Si es numérico, convertir
                            if pd.notna(value):
                                numeric_val = int(float(value))
                                return Sentiment.from_numeric(numeric_val).value
                            return value
                        except (ValueError, TypeError):
                            # Si ya es texto o no se puede convertir, retornar tal cual
                            return value
                    
                    # Solo convertir si los valores son numéricos
                    if df['Clasificacion'].dtype in ['int64', 'float64']:
                        df['Clasificacion'] = df['Clasificacion'].apply(convert_classification)
                    elif df['Clasificacion'].dtype == 'object':
                        # Verificar si hay valores numéricos mezclados con texto
                        numeric_mask = pd.to_numeric(df['Clasificacion'], errors='coerce').notna()
                        if numeric_mask.any():
                            df.loc[numeric_mask, 'Clasificacion'] = df.loc[numeric_mask, 'Clasificacion'].apply(convert_classification)
                
                return df
        except Error as e:
            print(f"Error al cargar el análisis '{name}': {e}")
            return pd.DataFrame()

    def delete_analysis(self, name: str) -> Tuple[bool, str]:
        """
        Elimina un análisis guardado de la base de datos MySQL.
        También intenta eliminar el archivo CSV asociado si existe.
        
        Args:
            name: El nombre de la tabla/análisis a eliminar.
            
        Returns:
            Tupla con (éxito, mensaje)
        """
        try:
            # Eliminar tabla de MySQL
            with mysql.connector.connect(**self._db_config) as conn:
                with conn.cursor() as cursor:
                    # Verificar que la tabla existe antes de intentar eliminarla
                    cursor.execute(f"SHOW TABLES LIKE '{name}'")
                    if not cursor.fetchone():
                        return False, f"El análisis '{name}' no existe en la base de datos."
                    
                    # Eliminar la tabla
                    cursor.execute(f"DROP TABLE IF EXISTS {name}")
                    conn.commit()
            
            # Intentar eliminar el archivo CSV asociado si existe
            # El nombre del archivo CSV se deriva del nombre de la tabla (sin el prefijo 'analisis_')
            csv_file_name = name.replace('analisis_', '') if name.startswith('analisis_') else name
            csv_path = os.path.join(self._csv_base_dir, f"{csv_file_name}_limpio.csv")
            
            csv_deleted = False
            if os.path.exists(csv_path):
                try:
                    os.remove(csv_path)
                    csv_deleted = True
                except Exception as e:
                    # No es crítico si no se puede eliminar el CSV
                    print(f"Advertencia: No se pudo eliminar el archivo CSV '{csv_path}': {e}")
            
            msg = f"Análisis '{name}' eliminado exitosamente de la base de datos."
            if csv_deleted:
                msg += f" Archivo CSV también eliminado."
            
            return True, msg
            
        except Error as e:
            return False, f"Error al eliminar el análisis '{name}': {e}"
        except Exception as e:
            return False, f"Error inesperado al eliminar el análisis '{name}': {e}"

    def delete_multiple_analyses(self, names: List[str]) -> Tuple[bool, List[Tuple[str, bool, str]]]:
        """
        Elimina múltiples análisis guardados de la base de datos MySQL.
        
        Args:
            names: Lista de nombres de análisis a eliminar.
            
        Returns:
            Tupla con (éxito_general, lista_de_resultados)
            donde cada resultado es (nombre, éxito, mensaje)
        """
        results = []
        all_success = True
        
        for name in names:
            success, message = self.delete_analysis(name)
            results.append((name, success, message))
            if not success:
                all_success = False
        
        return all_success, results
