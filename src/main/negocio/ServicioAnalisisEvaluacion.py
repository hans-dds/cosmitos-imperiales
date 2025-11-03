import pandas as pd
import joblib
import os
from negocio.ServicioAlmacenamiento import ServicioAlmacenamiento


class ServicioAnalisisEvaluacion:

    def __init__(self, ruta_modelo: str):

        try:
            self.modelo = joblib.load(ruta_modelo)
            print(f"Servicio de Análisis inicializado. "
                  f"Modelo cargado desde '{ruta_modelo}'.")

        except FileNotFoundError:
            print(f"ERROR CRÍTICO: No se encontró el archivo del modelo "
                  f"en la ruta '{ruta_modelo}'.")
            self.modelo = None

        except Exception as e:

            print(f"ERROR CRÍTICO: Falló joblib.load() por una razón "
                  f"inesperada: {e}")
            import traceback
            traceback.print_exc()
            self.modelo = None

        # ATENCION: Externalizar la configuración de la base de datos
        # en un entorno de producción
        db_config = {
            'host': 'localhost',
            'user': 'user',
            'password': 'password',
            'database': 'cosmitos_imperiales_db'
        }
        self.servicio_almacenamiento = ServicioAlmacenamiento(db_config=db_config)

    def realizar_analisis_sentimientos(self, datos: pd.DataFrame) -> pd.DataFrame:
        """
        Realiza análisis de sentimientos en los comentarios de un DataFrame.
        """
        if self.modelo is None:
            print("ERROR: El modelo no está cargado (self.modelo es None). "
                  "No se puede realizar la predicción.")
            return datos

        if not all(col in datos.columns for col in ['comentarios', 'calificacion']):
            print("ERROR: El DataFrame de entrada debe tener las columnas "
                  "'comentarios' y 'calificacion'.")
            return datos

        datos_a_predecir = datos.copy()
        datos_a_predecir.dropna(subset=['comentarios', 'calificacion'], inplace=True)

        if datos_a_predecir.empty:
            print("Advertencia: No hay datos válidos para predecir "
                  "después de eliminar nulos.")
            return datos

        X_para_predecir = datos_a_predecir[['comentarios', 'calificacion']]

        print(f"Realizando predicciones en {len(X_para_predecir)} filas...")
        predicciones = self.modelo.predict(X_para_predecir)

        datos_a_predecir['Clasificacion'] = predicciones

        print("Predicciones completadas.")
        return datos_a_predecir

    def guardar_analisis(self, datos: pd.DataFrame, nombre_base_archivo: str, nombre_tabla: str) -> tuple[bool, str]:
        """
        Guarda los resultados del análisis en un archivo CSV y en la base de datos MySQL.
        """
        print(f"Guardando análisis con nombre base '{nombre_base_archivo}' "
              f"y en tabla '{nombre_tabla}'...")

        guardado_csv, msg_csv = self.servicio_almacenamiento.guardar_analisis_csv(datos, nombre_base_archivo)
        guardado_mysql, msg_mysql = self.servicio_almacenamiento.guardar_analisis_mysql(datos, nombre_tabla)

        success = guardado_csv and guardado_mysql
        message = f"CSV: {msg_csv}\nMySQL: {msg_mysql}"

        return success, message

    def listar_analisis_guardados(self) -> list[str]:
        return self.servicio_almacenamiento.listar_analisis_guardados()

    def cargar_analisis_por_nombre(self, nombre_tabla: str) -> pd.DataFrame:
        return self.servicio_almacenamiento.cargar_analisis_por_nombre(nombre_tabla)


if __name__ == "__main__":

    # --- Configuración ---
    RUTA_MODELO_FINAL = 'clasificador_sentimiento_final.pkl'
    ARCHIVO_ENTRADA = 'comentarios_limpios_y_procesados.csv'
    NOMBRE_BASE_ARCHIVO_SALIDA = 'datos_con_prediccion_clase'
    NOMBRE_TABLA_SALIDA = 'analisis_sentimientos'

    try:
        servicio_analisis = ServicioAnalisisEvaluacion(ruta_modelo=RUTA_MODELO_FINAL)

        # 2. Cargar los datos que queremos clasificar
        df_a_predecir = pd.read_csv(ARCHIVO_ENTRADA)
        print(f"\nArchivo '{ARCHIVO_ENTRADA}' cargado para predicción.")

        # 3. Llamar al método para realizar el análisis
        df_con_predicciones = servicio_analisis.realizar_analisis_sentimientos(df_a_predecir)

        # 4. Mostrar y guardar los resultados
        print("\n--- Vista previa de los resultados ---")
        print(df_con_predicciones.head().to_string())

        # 5. Guardar los resultados
        success, message = servicio_analisis.guardar_analisis(
            df_con_predicciones, NOMBRE_BASE_ARCHIVO_SALIDA, NOMBRE_TABLA_SALIDA
        )
        print(message)

    except Exception as e:
        print(f"Ocurrió un error en el proceso principal: {e}")