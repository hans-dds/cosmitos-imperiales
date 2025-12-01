import os
from typing import List, Tuple

import mysql.connector
import pandas as pd
from mysql.connector import Error

from use_cases.ports.analysis_repository import IAnalysisRepository


class SQLandCSVAnalysisRepository(IAnalysisRepository):
    """Repositorio compuesto que persiste análisis en CSV y MySQL.

    Encapsula detalles de cada medio y expone una interfaz agnóstica.
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

    def _save_csv(self, data: pd.DataFrame, analysis_id: str) -> Tuple[bool, str]:
        if data.empty:
            return False, "No se proporcionaron datos para guardar."
        file_path = os.path.join(self._csv_base_dir, f"{analysis_id}_limpio.csv")
        try:
            data.to_csv(file_path, index=False, encoding='utf-8-sig')
            return True, f"Datos guardados exitosamente en '{file_path}'."
        except Exception as e:
            return False, f"Fallo al guardar el archivo CSV. Razón: {e}"

    def _save_mysql(self, data: pd.DataFrame, table_name: str) -> Tuple[bool, str]:
        try:
            with mysql.connector.connect(**self._db_config) as conn:
                with conn.cursor() as cursor:
                    if not all(c.isalnum() or c == '_' for c in table_name):
                        return False, f"Nombre de tabla inválido: {table_name}"
                    self._ensure_table_exists(cursor, table_name)
                    base_columns = ["comentarios", "calificacion", "Clasificacion", "Fiabilidad"]
                    insert_columns = list(base_columns)
                    has_fecha = 'fecha' in data.columns
                    if has_fecha:
                        insert_columns.append('fecha')
                    placeholders = ", ".join(["%s"] * len(insert_columns))
                    sql = (
                        f"INSERT INTO `{table_name}` (" + ", ".join(insert_columns) + ") VALUES (" + placeholders + ")"
                    )
                    for _, row in data.iterrows():
                        fiabilidad = row.get('Fiabilidad', 'N/A')
                        if isinstance(fiabilidad, (int, float)):
                            fiabilidad = str(fiabilidad)
                        values = [row['comentarios'], row['calificacion'], row['Clasificacion'], fiabilidad]
                        if has_fecha:
                            fecha_val = row.get('fecha')
                            if pd.notna(fecha_val) and hasattr(fecha_val, 'date'):
                                fecha_val = fecha_val.date()
                            elif pd.isna(fecha_val):
                                fecha_val = None
                            else:
                                try:
                                    fecha_val = pd.to_datetime(fecha_val).date()
                                except ValueError:
                                    fecha_val = None
                            values.append(fecha_val)
                        cursor.execute(sql, values)
                    conn.commit()
            return True, f"Datos guardados exitosamente en la tabla MySQL '{table_name}'."
        except Error as e:
            return False, f"Error al conectar o guardar en MySQL: {e}"

    def list(self) -> List[str]:
        try:
            with mysql.connector.connect(**self._db_config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SHOW TABLES LIKE 'analisis_%'")
                    return [row[0] for row in cursor.fetchall()]
        except Error:
            return []

    def load(self, analysis_id: str) -> pd.DataFrame:
        try:
            with mysql.connector.connect(**self._db_config) as conn:
                if not all(c.isalnum() or c == '_' for c in analysis_id):
                    return pd.DataFrame()
                query = f"SELECT * FROM `{analysis_id}`"
                df = pd.read_sql(query, conn)
                return df
        except Error:
            return pd.DataFrame()

    def delete(self, analysis_id: str) -> Tuple[bool, str]:
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
                    if not all(c.isalnum() or c == '_' for c in analysis_id):
                        return False, f"Nombre de tabla inválido: {analysis_id}"
                    cursor.execute(f"SHOW TABLES LIKE '{analysis_id}'")
                    if not cursor.fetchone():
                        return False, f"El análisis '{analysis_id}' no existe en la base de datos."
                    cursor.execute(f"DROP TABLE IF EXISTS `{analysis_id}`")
                    conn.commit()
            # Intentar eliminar el archivo CSV asociado si existe
            # El nombre del archivo CSV se deriva del nombre de la tabla
            # (sin el prefijo 'analisis_')
            csv_file_name = analysis_id.replace('analisis_', '') if analysis_id.startswith('analisis_') else analysis_id
            csv_path = os.path.join(
                self._csv_base_dir, f"{csv_file_name}_limpio.csv")
            csv_deleted = False
            if os.path.exists(csv_path):
                try:
                    os.remove(csv_path)
                    csv_deleted = True
                except Exception as e:
                    # No es crítico si no se puede eliminar el CSV
                    print("Advertencia: No se pudo eliminar el archivo CSV"
                          f" '{csv_path}': {e}")
            # Mensaje base de eliminación exitosa
            msg = (f"Análisis '{analysis_id}' eliminado exitosamente de la base de datos.")
            if csv_deleted:
                msg += " Archivo CSV también eliminado."
            return True, msg
        except Error as e:
            return False, f"Error al eliminar el análisis '{analysis_id}': {e}"
        except Exception as e:
            return False, f"Error inesperado al eliminar el análisis '{analysis_id}': {e}"

    def delete_many(self, analysis_ids: List[str]) -> Tuple[bool, List[Tuple[str, bool, str]]]:
        results: List[Tuple[str, bool, str]] = []
        all_success = True
        for aid in analysis_ids:
            success, message = self.delete(aid)
            results.append((aid, success, message))
            if not success:
                all_success = False
        return all_success, results

    def save(self, data: pd.DataFrame, analysis_id: str) -> Tuple[bool, str]:
        table_name = f"analisis_{analysis_id}" if not analysis_id.startswith('analisis_') else analysis_id
        ok_csv, msg_csv = self._save_csv(data, analysis_id)
        ok_sql, msg_sql = self._save_mysql(data, table_name)
        if ok_csv and ok_sql:
            return True, "Persistencia realizada en CSV y MySQL."
        if ok_csv and not ok_sql:
            return False, f"CSV OK. MySQL fallo: {msg_sql}"
        if ok_sql and not ok_csv:
            return False, f"MySQL OK. CSV fallo: {msg_csv}"
        return False, f"Fallos: CSV={msg_csv}; MySQL={msg_sql}"

    def _ensure_table_exists(self, cursor, table_name: str) -> None:
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS `{table_name}` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            comentarios TEXT,
            calificacion FLOAT,
            Clasificacion VARCHAR(255),
            Fiabilidad VARCHAR(255),
            fecha DATE NULL
        )""")

