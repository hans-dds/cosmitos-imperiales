import pandas as pd
import mysql.connector
from mysql.connector import Error
from datos.GuardarDatosArchivo import GuardarDatosArchivo


class ServicioAlmacenamiento:
    """
    Servicio para almacenar y recuperar análisis de datos.
    Proporciona métodos para guardar análisis en archivos CSV
    y en una base de datos MySQL,
    así como para listar y cargar análisis guardados.
    """
    def __init__(self, db_config, directorio_base_csv='datos_analizados'):
        """
        Inicializa el servicio con la configuración de la base de datos y
        el directorio base para guardar archivos CSV.
        """
        self.db_config = db_config
        self.guardar_datos_csv = GuardarDatosArchivo(
            directorio_base=directorio_base_csv
        )

    def guardar_analisis_csv(
        self,
        datos: pd.DataFrame,
        nombre_archivo: str
    ) -> tuple:
        """
        Guarda los datos del análisis en un archivo CSV.

        Args:
            datos (pd.DataFrame): Datos del análisis a guardar.
            nombre_archivo (str): Nombre del archivo CSV donde se
            guardarán los datos.
        Returns:
            tuple: (bool, str) indicando éxito y mensaje correspondiente.
        Raises:
            Exception: Si ocurre un error al guardar el archivo CSV.
        """
        return self.guardar_datos_csv.guardar_datos_limpios(
            datos,
            nombre_archivo
        )

    def guardar_analisis_mysql(
        self,
        datos: pd.DataFrame,
        nombre_tabla: str
    ) -> tuple:
        """
        Guarda los datos del análisis en una tabla de MySQL.

        Args:
            datos (pd.DataFrame): Datos del análisis a guardar.
            nombre_tabla (str): Nombre de la tabla donde se guardarán los
            datos.
        Returns:
            tuple: (bool, str) indicando éxito y mensaje correspondiente.
        Raises:
            Error: Si ocurre un error al conectar o guardar en la base de
            datos.
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
                        val = (
                            row['comentarios'],
                            row['calificacion'],
                            row['Clasificacion']
                        )
                        cursor.execute(sql, val)
                    conn.commit()
            msg = (
                f"Datos guardados exitosamente en la tabla "
                f"'{nombre_tabla}' de MySQL."
            )
            print(msg)
            return True, msg
        except Error as e:
            msg = f"Error al conectar o guardar en MySQL: {e}"
            print(msg)
            return False, msg

    def listar_analisis_guardados(self) -> list:
        """
        Lista las tablas de análisis guardados en la base de datos.

        Returns:
            list: Lista de nombres de tablas de análisis guardados.
        Raises:
            Error: Si ocurre un error al conectar o consultar la base de datos.
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

        Args:
            nombre_tabla (str): Nombre de la tabla de análisis a cargar.
        Returns:
            pd.DataFrame: Datos del análisis cargados en un DataFrame.
        Raises:
            Error: Si ocurre un error al conectar o consultar la base de datos.
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
            msg = (
                f"Error al cargar los datos del análisis "
                f"'{nombre_tabla}': {e}"
            )
            print(msg)
            return pd.DataFrame()
