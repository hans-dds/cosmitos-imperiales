import mysql.connector
from mysql.connector import Error
from typing import List, Tuple, Dict
from use_cases.ports.note_repository import INoteRepository


class SQLNoteRepository(INoteRepository):
    def __init__(self, db_config: dict):
        self._db_config = db_config

    def _ensure_table_exists(self, cursor):
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS `report_notes` (
                id INT AUTO_INCREMENT PRIMARY KEY,
                analysis_name VARCHAR(255) NOT NULL,
                note_content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

    def add(self, analysis_name: str, content: str) -> Tuple[bool, str]:
        try:
            with mysql.connector.connect(**self._db_config) as conn:
                with conn.cursor() as cursor:
                    self._ensure_table_exists(cursor)
                    sql = "INSERT INTO report_notes (analysis_name, note_content) VALUES (%s, %s)"
                    cursor.execute(sql, (analysis_name, content))
                conn.commit()
            return True, "Nota guardada."
        except Error as e:
            return False, f"Error BD: {e}"

    def get_all(self, analysis_name: str) -> List[Dict]:
        try:
            with mysql.connector.connect(**self._db_config) as conn:
                with conn.cursor(dictionary=True) as cursor:
                    self._ensure_table_exists(cursor)
                    sql = "SELECT * FROM report_notes WHERE analysis_name = %s ORDER BY created_at DESC"
                    cursor.execute(sql, (analysis_name,))
                    return cursor.fetchall()
        except Error:
            return []

    def delete(self, note_id: int) -> Tuple[bool, str]:
        try:
            with mysql.connector.connect(**self._db_config) as conn:
                with conn.cursor() as cursor:
                    self._ensure_table_exists(cursor)
                    cursor.execute(
                        "DELETE FROM report_notes WHERE id = %s", (note_id,)
                    )
                conn.commit()
            return True, "Nota eliminada."
        except Error as e:
            return False, f"Error BD: {e}"
