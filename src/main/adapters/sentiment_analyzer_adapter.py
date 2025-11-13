import joblib
import pandas as pd

from use_cases.ports.sentiment_analyzer import ISentimentAnalyzer


class JoblibSentimentAnalyzer(ISentimentAnalyzer):
    """
    Una implementación concreta de ISentimentAnalyzer que utiliza un modelo
    cargado desde un archivo .pkl con joblib.
    """

    def __init__(self, model_path: str):
        try:
            self._model = joblib.load(model_path)
            print(f"Modelo de análisis de sentimiento cargado desde '{model_path}'.")
        except FileNotFoundError:
            raise RuntimeError(
                f"CRÍTICO: No se encontró el archivo del modelo en '{model_path}'.")
        except Exception as e:
            raise RuntimeError(
                f"CRÍTICO: Falló la carga del modelo desde '{model_path}'.\n"
                f"Razón: {e}")

    def analyze(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Realiza análisis de sentimiento utilizando el modelo joblib cargado.
        """
        if not all(col in data.columns
                   for col in ['comentarios', 'calificacion']):
            raise ValueError("El DataFrame de entrada debe tener las columnas"
                             " 'comentarios' y 'calificacion'.")

        if data.empty:
            print("Advertencia: No hay datos para analizar.")
            return data

        # El modelo espera columnas específicas para la predicción
        X_to_predict = data[['comentarios', 'calificacion']]

        predictions = self._model.predict(X_to_predict)

        analyzed_df = data.copy()
        analyzed_df['Clasificacion'] = predictions

        return analyzed_df
