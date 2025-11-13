import joblib
import pandas as pd

from use_cases.ports.sentiment_analyzer import ISentimentAnalyzer


class JoblibSentimentAnalyzer(ISentimentAnalyzer):
    """
    A concrete implementation of ISentimentAnalyzer that uses a model
    loaded from a .pkl file with joblib.
    """

    def __init__(self, model_path: str):
        try:
            self._model = joblib.load(model_path)
            print(f"Sentiment analysis model loaded from '{model_path}'.")
        except FileNotFoundError:
            raise RuntimeError(
                f"CRITICAL: Model file not found at '{model_path}'.")
        except Exception as e:
            raise RuntimeError(
                f"CRITICAL: Failed to load model from '{model_path}'.\n"
                f"Reason: {e}")

    def analyze(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Performs sentiment analysis using the loaded joblib model.
        """
        if not all(col in data.columns
                   for col in ['comentarios', 'calificacion']):
            raise ValueError("Input DataFrame must have 'comentarios'"
                             " and 'calificacion' columns.")

        if data.empty:
            print("Warning: No data to analyze.")
            return data

        # The model expects specific columns for prediction
        X_to_predict = data[['comentarios', 'calificacion']]

        predictions = self._model.predict(X_to_predict)

        analyzed_df = data.copy()
        analyzed_df['Clasificacion'] = predictions

        return analyzed_df
