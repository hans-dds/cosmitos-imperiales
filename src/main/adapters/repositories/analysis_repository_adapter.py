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
        """Carga un análisis específico de una tabla de MySQL."""
        try:
            with mysql.connector.connect(**self._db_config) as conn:
                query = (f"SELECT comentarios, calificacion, Clasificacion "
                         f"FROM {name}")
                return pd.read_sql(query, conn)
        except Error as e:
            print(f"Error al cargar el análisis '{name}': {e}")
            return pd.DataFrame()
