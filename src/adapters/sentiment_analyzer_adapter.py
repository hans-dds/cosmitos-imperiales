import joblib
import pandas as pd

from domain.value_objects.sentiment import Sentiment
from use_cases.ports.sentiment_analyzer import ISentimentAnalyzer


class JoblibSentimentAnalyzer(ISentimentAnalyzer):
    """
    Una implementación concreta de ISentimentAnalyzer que utiliza un modelo
    cargado desde un archivo .pkl con joblib.
    Convierte los valores numéricos del modelo (-1, 0, 1) a etiquetas de texto
    usando el Value Object Sentiment del dominio.
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
        Convierte los valores numéricos del modelo a etiquetas de texto del dominio.
        
        Args:
            data: DataFrame con columnas 'comentarios' y 'calificacion'
            
        Returns:
            DataFrame con la columna 'Clasificacion' agregada con valores de texto
            ("Detractor", "Neutro", "Promotor")
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

        # Obtener predicciones numéricas del modelo (-1, 0, o 1)
        numeric_predictions = self._model.predict(X_to_predict)

        # Convertir valores numéricos a etiquetas de texto usando el Value Object del dominio
        analyzed_df = data.copy()
        analyzed_df['Clasificacion'] = [
            Sentiment.from_numeric(int(pred)).value 
            for pred in numeric_predictions
        ]

        return analyzed_df
