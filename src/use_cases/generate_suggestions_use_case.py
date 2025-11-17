import pandas as pd
from typing import List, Optional

from use_cases.ports.suggestion_generator import ISuggestionGenerator
from use_cases.ports.analysis_repository import IAnalysisRepository
from domain.entities.suggestion import Suggestion
from domain.value_objects.sentiment import Sentiment

class GenerateSuggestionsUseCase:
    """
    Este caso de uso orquesta la generación de sugerencias de mejora
    basadas en los comentarios de los detractores.
    """

    def __init__(
        self,
        suggestion_generator: ISuggestionGenerator,
        analysis_repository: IAnalysisRepository
    ):
        self._suggestion_generator = suggestion_generator
        self._analysis_repository = analysis_repository

    def execute(self, analysis_name: str) -> List[Suggestion]:
        """
        Ejecuta el caso de uso.

        Args:
            analysis_name: El nombre del análisis a cargar.

        Returns:
            Una lista de Sugerencias.
        """
        
        # 1. Cargar el análisis guardado
        # Usamos el repositorio existente para cargar los datos
        try:
            analysis_df = self._analysis_repository.load_analysis(analysis_name)
        except Exception as e:
            print(f"Error al cargar análisis {analysis_name}: {e}")
            # Devolver una lista vacía si falla la carga
            return []

        if analysis_df.empty:
            return []

        # 2. Filtrar solo comentarios de Detractores (Criterio de Aceptación)
        # Usamos el Value Object de Dominio para la comparación
        detractor_comments_df = analysis_df[
            analysis_df['Clasificacion'] == Sentiment.DETRACTOR.value
        ]

        if detractor_comments_df.empty:
            # Si no hay detractores, no hay nada que analizar
            return []

        # 3. Obtener la lista de comentarios
        comments_list = detractor_comments_df['comentarios'].dropna().tolist()

        if not comments_list:
            return []

        # 4. Generar sugerencias (delegando al puerto)
        suggestions = self._suggestion_generator.generate_suggestions(comments_list)
        
        # 5. Aplicar lógica de negocio (Criterios de Aceptación)
        # Devolver solo las 3 principales
        return suggestions[:3]
