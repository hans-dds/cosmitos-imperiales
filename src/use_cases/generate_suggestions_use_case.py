import pandas as pd
from typing import List, Dict
from use_cases.ports.suggestion_generator import ISuggestionGenerator
from domain.value_objects.sentiment import Sentiment

class GenerateSuggestionsUseCase:
    def __init__(self, suggestion_generator: ISuggestionGenerator):
        self._generator = suggestion_generator

    def execute(self, df: pd.DataFrame) -> List[Dict[str, str]]:
        if df.empty or 'Clasificacion' not in df.columns:
            return []

        # Filtrar solo detractores (Lógica de la HU)
        detractors = df[
            (df['Clasificacion'] == Sentiment.DETRACTOR.value) | 
            (df['Clasificacion'] == 'Detractor')
        ]
        
        comments = detractors['comentarios'].dropna().tolist()
        
        if not comments:
            return []

        return self._generator.generate(comments)