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
                    # Validar que el nombre de la tabla solo contiene caracteres alfanuméricos y guiones bajos
                    if not all(c.isalnum() or c == '_' for c in table_name):
                        raise ValueError(f"Nombre de tabla inválido: {table_name}")
                    
                    # Esta es una creación de esquema simplificada
                    # Usar backticks para escapar el nombre de la tabla
                    cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS `{table_name}` (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        comentarios TEXT,
                        calificacion FLOAT,
                        Clasificacion VARCHAR(255),
                        Fiabilidad VARCHAR(255),
                        fecha DATE NULL
                    )""")

                    # Construir la sentencia de inserción dinámicamente para
                    # mantener compatibilidad con datos sin columna de fecha.
                    base_columns = ["comentarios", "calificacion", "Clasificacion", "Fiabilidad"]
                    insert_columns = list(base_columns)
                    has_fecha = 'fecha' in data.columns
                    if has_fecha:
                        insert_columns.append('fecha')
                    
                    placeholders = ", ".join(["%s"] * len(insert_columns))
                    sql = (
                        f"INSERT INTO `{table_name}` "
                        f"({', '.join(insert_columns)}) "
                        f"VALUES ({placeholders})"
                    )

                    for _, row in data.iterrows():
                        # Asegurar que Fiabilidad existe en el row
                        fiabilidad = row.get('Fiabilidad', 'N/A')
                        # Convertir a string si es numérico
                        if isinstance(fiabilidad, (int, float)):
                            fiabilidad = str(fiabilidad)
                        
                        values = [
                            row['comentarios'],
                            row['calificacion'],
                            row['Clasificacion'],
                            fiabilidad,
                        ]
                        
                        if has_fecha:
                            # Si la columna está en datetime, extraer solo la fecha;
                            # si no, dejar que el conector intente convertirla.
                            fecha_val = row.get('fecha')
                            if pd.notna(fecha_val) and hasattr(fecha_val, 'date'):
                                fecha_val = fecha_val.date()
                            elif pd.isna(fecha_val):
                                fecha_val = None
                            else:
                                # Intentar convertir si es string u otro tipo
                                try:
                                    fecha_val = pd.to_datetime(fecha_val).date()
                                except:
                                    fecha_val = None
                            values.append(fecha_val)
                        
                        cursor.execute(sql, values)
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
        Agrega columna de Fiabilidad si no existe.
        """
        try:
            with mysql.connector.connect(**self._db_config) as conn:
                # Usar parámetros preparados para mayor seguridad
                # Validar que el nombre de la tabla solo contiene caracteres alfanuméricos y guiones bajos
                if not all(c.isalnum() or c == '_' for c in name):
                    raise ValueError(f"Nombre de tabla inválido: {name}")
                
                # Seleccionamos todas las columnas para permitir que columnas
                # adicionales (como 'fecha') estén disponibles para la capa de UI.
                query = f"SELECT * FROM `{name}`"
                df = pd.read_sql(query, conn)
                
                # Usar el mapper para convertir clasificaciones
                if not df.empty and 'Clasificacion' in df.columns:
                    from use_cases.mappers.sentiment_mapper import convert_dataframe_classifications
                    df = convert_dataframe_classifications(df)
                
                # Agregar Fiabilidad si no existe
                if 'Fiabilidad' not in df.columns:
                    df['Fiabilidad'] = 'N/A'
                
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
                    # Validar que el nombre de la tabla solo contiene caracteres alfanuméricos y guiones bajos
                    if not all(c.isalnum() or c == '_' for c in name):
                        return False, f"Nombre de tabla inválido: {name}"
                    
                    # Verificar que la tabla existe antes de intentar eliminarla
                    cursor.execute(f"SHOW TABLES LIKE '{name}'")
                    if not cursor.fetchone():
                        return False, f"El análisis '{name}' no existe en la base de datos."
                    
                    # Eliminar la tabla usando backticks para escapar
                    cursor.execute(f"DROP TABLE IF EXISTS `{name}`")
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
