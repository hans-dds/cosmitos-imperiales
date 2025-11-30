import joblib
import pandas as pd

from domain.value_objects.sentiment import Sentiment
from domain.services.reliability_calculator import (
    calculate_reliability_from_probability,
    calculate_reliability_from_rating
)
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
            print("Modelo de análisis de sentimiento cargado desde"
                  f" '{model_path}'.")
        except FileNotFoundError:
            raise RuntimeError(
                "CRÍTICO: No se encontró el archivo del modelo en"
                f" '{model_path}'.")
        except Exception as e:
            raise RuntimeError(
                "CRÍTICO: Falló la carga del modelo desde"
                f" '{model_path}'.\n"
                f"Razón: {e}")

    def analyze(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Realiza análisis de sentimiento utilizando el modelo joblib cargado.
        Convierte los valores numéricos del modelo a etiquetas de texto
        del dominio.
        Args:
            data: DataFrame con columnas 'comentarios' y 'calificacion'
        Returns:
            DataFrame con la columna 'Clasificacion' agregada con valores
            de texto ("Detractor", "Neutro", "Promotor")
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
        # Convertir valores numéricos a etiquetas de texto usando el
        # Value Object del dominio
        analyzed_df = data.copy()
        analyzed_df['Clasificacion'] = [
            Sentiment.from_numeric(int(pred)).value
            for pred in numeric_predictions
        ]
        # Calcular fiabilidad
        analyzed_df = self._add_reliability(analyzed_df, X_to_predict)
        return analyzed_df

    def _add_reliability(
            self,
            df: pd.DataFrame,
            X_to_predict: pd.DataFrame) -> pd.DataFrame:
        """
        Agrega la columna de fiabilidad al DataFrame.
        Si el modelo tiene predict_proba, usa las probabilidades máximas.
        Si no, usa la calificación como fallback.
        Args:
            df: DataFrame con las predicciones
            X_to_predict: Datos usados para la predicción
        Returns:
            DataFrame con la columna 'Fiabilidad' agregada
        """
        if hasattr(self._model, 'predict_proba'):
            try:
                # Obtener probabilidades de todas las clases
                probabilities = self._model.predict_proba(X_to_predict)
                # Obtener la probabilidad máxima para cada predicción
                max_probabilities = probabilities.max(axis=1)
                # Convertir a fiabilidad numérica
                df['Fiabilidad'] = [
                    calculate_reliability_from_probability(float(prob))
                    for prob in max_probabilities
                ]
            except Exception as e:
                print("Advertencia: No se pudieron obtener probabilidades"
                      f" del modelo: {e}")
                # Fallback a calificación
                df['Fiabilidad'] = df['calificacion'].apply(
                    calculate_reliability_from_rating)
        else:
            # Usar calificación como fallback
            df['Fiabilidad'] = df['calificacion'].apply(
                calculate_reliability_from_rating)
        return df
