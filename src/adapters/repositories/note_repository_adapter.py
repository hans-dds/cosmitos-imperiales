import mysql.connector
from mysql.connector import Error
from typing import List, Dict
from use_cases.ports.note_repository import INoteRepository

class MySQLNoteRepository(INoteRepository):
    def __init__(self, db_config: dict):
        self._db_config = db_config

    def _get_connection(self):
        return mysql.connector.connect(**self._db_config)

    def add_note(self, analysis_name: str, content: str) -> bool:
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            query = "INSERT INTO notas_analisis (nombre_analisis, contenido) VALUES (%s, %s)"
            cursor.execute(query, (analysis_name, content))
            conn.commit()
            return True
        except Error as e:
            print(f"Error al guardar nota: {e}")
            return False
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def get_notes(self, analysis_name: str) -> List[Dict]:
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT id, contenido, fecha_creacion FROM notas_analisis WHERE nombre_analisis = %s ORDER BY fecha_creacion DESC"
            cursor.execute(query, (analysis_name,))
            return cursor.fetchall()
        except Error as e:
            print(f"Error al obtener notas: {e}")
            return []
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def delete_note(self, note_id: int) -> bool:
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            query = "DELETE FROM notas_analisis WHERE id = %s"
            cursor.execute(query, (note_id,))
            conn.commit()
            return True
        except Error:
            return False
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def update_note(self, note_id: int, new_content: str) -> bool:
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            query = "UPDATE notas_analisis SET contenido = %s WHERE id = %s"
            cursor.execute(query, (new_content, note_id))
            conn.commit()
            return True
        except Error:
            return False
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()