import os
from typing import List, Optional, Tuple

import mysql.connector
from mysql.connector import Error

from use_cases.ports.report_repository import IReportRepository


class SQLReportRepository(IReportRepository):
    """
    Implementación que almacena historial de reportes en MySQL y guarda
    archivos en disco bajo un directorio configurable.
    """

    def __init__(self, db_config: dict, reports_base_dir: str = "reports"):
        self._db_config = db_config
        self._reports_base_dir = reports_base_dir
        os.makedirs(self._reports_base_dir, exist_ok=True)
        self._ensure_table()

    def _ensure_table(self) -> None:
        try:
            with mysql.connector.connect(**self._db_config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS report_history (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            analysis_name VARCHAR(255) NOT NULL,
                            report_format VARCHAR(16) NOT NULL,
                            file_path VARCHAR(1024) NOT NULL,
                            source_file_name VARCHAR(255) NULL,
                            date_range VARCHAR(255) NULL,
                            comments_count INT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                        """
                    )
                conn.commit()
        except Error:
            # Silencioso: se manejará al guardar/listar
            pass

    def _fetch_all_paths(self) -> List[str]:
        """Obtiene todas las rutas de archivos registradas en el historial."""
        try:
            with mysql.connector.connect(**self._db_config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT file_path FROM report_history")
                    return [
                        row[0] for row in cursor.fetchall() if row and row[0]
                    ]
        except Error:
            return []

    def _delete_files(self, paths: List[str]) -> int:
        """Elimina archivos de disco de forma segura. Devuelve el conteo eliminado."""
        deleted = 0
        for p in set(paths):
            try:
                if p and os.path.exists(p):
                    os.remove(p)
                    deleted += 1
            except Exception:
                # Continuar sin bloquear por errores de FS
                continue
        return deleted

    def save(
        self,
        analysis_name: str,
        report_format: str,
        file_path: str,
        source_file_name: str = None,
        date_range: str = None,
        comments_count: int = None,
    ) -> Tuple[bool, str]:
        try:
            with mysql.connector.connect(**self._db_config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO report_history (analysis_name, report_format, file_path, source_file_name, date_range, comments_count)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (
                            analysis_name,
                            report_format,
                            file_path,
                            source_file_name,
                            date_range,
                            comments_count,
                        ),
                    )
                conn.commit()
            return True, "Reporte guardado en historial"
        except Error as e:
            return False, f"Error al guardar historial en MySQL: {e}"

    def list(self) -> List[dict]:
        try:
            with mysql.connector.connect(**self._db_config) as conn:
                query = "SELECT id, analysis_name, report_format, file_path, source_file_name, date_range, comments_count, created_at FROM report_history ORDER BY created_at DESC"
                rows = []
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query)
                    rows = cursor.fetchall()
                return rows or []
        except Error:
            return []

    def get(self, report_id: int) -> Optional[dict]:
        try:
            with mysql.connector.connect(**self._db_config) as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(
                        "SELECT id, analysis_name, report_format, file_path, source_file_name, date_range, comments_count, created_at FROM report_history WHERE id=%s",
                        (report_id,),
                    )
                    row = cursor.fetchone()
                return row
        except Error:
            return None

    def clear(self) -> Tuple[bool, str]:
        """Elimina el historial y borra los archivos almacenados en reports/."""
        try:
            # Obtener y eliminar archivos del disco (SRP: métodos privados dedicados)
            paths = self._fetch_all_paths()
            deleted_count = self._delete_files(paths)

            # Limpiar tabla
            with mysql.connector.connect(**self._db_config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("TRUNCATE TABLE report_history")
                conn.commit()

            return (
                True,
                f"Historial limpiado. Archivos eliminados: {deleted_count}",
            )
        except Error as e:
            return False, f"Error al limpiar historial: {e}"

    def delete(self, report_id: int) -> Tuple[bool, str]:
        """Elimina un registro del historial y su archivo asociado si existe."""
        try:
            # Obtener metadatos para conocer la ruta
            with mysql.connector.connect(**self._db_config) as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(
                        "SELECT file_path FROM report_history WHERE id=%s",
                        (report_id,),
                    )
                    row = cursor.fetchone()
                file_path = row.get("file_path") if row else None

            # Eliminar archivo
            deleted_file = 0
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    deleted_file = 1
                except Exception:
                    deleted_file = 0

            # Eliminar fila
            with mysql.connector.connect(**self._db_config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM report_history WHERE id=%s", (report_id,)
                    )
                conn.commit()

            return (
                True,
                f"Reporte eliminado. Archivos borrados: {deleted_file}",
            )
        except Error as e:
            return False, f"Error al eliminar reporte: {e}"
