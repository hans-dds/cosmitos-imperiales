import pandas as pd
import mysql.connector
from mysql.connector import Error
from datos.GuardarDatosArchivo import GuardarDatosArchivo


class ServicioAlmacenamiento:
    def __init__(self, db_config, directorio_base_csv='datos_analizados'):
        self.db_config = db_config
        self.guardar_datos_csv = GuardarDatosArchivo(
            directorio_base=directorio_base_csv
        )

    def guardar_analisis_csv(self, datos: pd.DataFrame, nombre_archivo: str) -> tuple[bool, str]:
        """
        Guarda los datos del análisis en un archivo CSV.
        """
        return self.guardar_datos_csv.guardar_datos_limpios(datos, nombre_archivo)

    def guardar_analisis_mysql(self, datos: pd.DataFrame, nombre_tabla: str) -> tuple[bool, str]:
        """
        Guarda los datos del análisis en una tabla de MySQL.
        """
        try:
            with mysql.connector.connect(**self.db_config) as conn:
                with conn.cursor() as cursor:
                    create_table_query = f"""
                    CREATE TABLE IF NOT EXISTS {nombre_tabla} (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        comentarios TEXT,
                        calificacion FLOAT,
                        Clasificacion VARCHAR(255)
                    )
                    """
                    cursor.execute(create_table_query)

                    for i, row in datos.iterrows():
                        sql = (
                            f"INSERT INTO {nombre_tabla} "
                            "(comentarios, calificacion, Clasificacion) "
                            "VALUES (%s, %s, %s)"
                        )
                        val = (row['comentarios'], row['calificacion'], row['Clasificacion'])
                        cursor.execute(sql, val)
                    conn.commit()
            msg = f"Datos guardados exitosamente en la tabla '{nombre_tabla}' de MySQL."
            print(msg)
            return True, msg
        except Error as e:
            msg = f"Error al conectar o guardar en MySQL: {e}"
            print(msg)
            return False, msg

    def listar_analisis_guardados(self) -> list[str]:
        """
        Lista las tablas de análisis guardados en la base de datos.
        """
        try:
            with mysql.connector.connect(**self.db_config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SHOW TABLES LIKE 'analisis_%'")
                    tablas = [row[0] for row in cursor.fetchall()]
                    return tablas
        except Error as e:
            print(f"Error al listar las tablas de análisis: {e}")
            return []

    def cargar_analisis_por_nombre(self, nombre_tabla: str) -> pd.DataFrame:
        """
        Carga los datos de una tabla de análisis específica.
        """
        try:
            with mysql.connector.connect(**self.db_config) as conn:
                query = (
                    f"SELECT comentarios, calificacion, Clasificacion "
                    f"FROM {nombre_tabla}"
                )
                df = pd.read_sql(query, conn)
                return df
        except Error as e:
            print(f"Error al cargar los datos del análisis '{nombre_tabla}': {e}")
            return pd.DataFrame()
