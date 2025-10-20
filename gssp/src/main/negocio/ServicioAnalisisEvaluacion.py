import pandas as pd
import joblib
import os



class ServicioAnalisisEvaluacion:

    def __init__(self, ruta_modelo='../negocio/clasificador_sentimiento_final.pkl'):
        """
        Args:
            ruta_modelo (str): La ruta al archivo .pkl del modelo entrenado.
        """

        try:
            self.modelo = joblib.load(ruta_modelo)
            print(f"Servicio de Análisis inicializado. Modelo cargado desde '{ruta_modelo}'.")
        except FileNotFoundError:
            print(f"ERROR CRÍTICO: No se encontró el archivo del modelo en la ruta '{ruta_modelo, os.getcwd(), os.listdir(os.getcwd())}'.")
            self.modelo = None
            raise
    
    def realizar_analisis_sentimientos(self, datos: pd.DataFrame) -> pd.DataFrame:
        """
        Realiza análisis de sentimientos en los comentarios de un DataFrame.

        Args:
            datos (pd.DataFrame): DataFrame que debe contener las columnas 'comentarios' y 'calificacion'.

        Returns:
            pd.DataFrame: El mismo DataFrame de entrada con la columna 'Clasificacion' añadida.
        """
        if self.modelo is None:
            print("ERROR: El modelo no está cargado. No se puede realizar la predicción.")
            return datos

        # 1. Validar que los datos de entrada son correctos
        if not all(col in datos.columns for col in ['comentarios', 'calificacion']):
            print("ERROR: El DataFrame de entrada debe tener las columnas 'comentarios' y 'calificacion'.")
            return datos
        
        datos_a_predecir = datos.copy()
        datos_a_predecir.dropna(subset=['comentarios', 'calificacion'], inplace=True)

        if datos_a_predecir.empty:
            print("Advertencia: No hay datos válidos para predecir después de eliminar nulos.")
            return datos

        X_para_predecir = datos_a_predecir[['comentarios', 'calificacion']]
        
        print(f"Realizando predicciones en {len(X_para_predecir)} filas...")
        predicciones = self.modelo.predict(X_para_predecir)
        
        datos_a_predecir['Clasificacion'] = predicciones
        
        print("Predicciones completadas.")
        return datos_a_predecir

if __name__ == "__main__":
    
    # --- Configuración ---
    RUTA_MODELO_FINAL = 'clasificador_sentimiento_final.pkl'
    ARCHIVO_ENTRADA = 'comentarios_limpios_y_procesados.csv'
    ARCHIVO_SALIDA = 'datos_con_prediccion_clase.csv'
    
    # 1. Crear una instancia del servicio. El modelo se carga aquí, UNA SOLA VEZ.
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
        
        df_con_predicciones.to_csv(ARCHIVO_SALIDA, index=False, encoding='utf-8-sig')
        print(f"\nResultados guardados exitosamente en '{ARCHIVO_SALIDA}'.")

    except Exception as e:
        print(f"Ocurrió un error en el proceso principal: {e}")