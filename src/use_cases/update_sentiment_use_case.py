"""Caso de uso para actualizar etiquetas de sentimiento manualmente."""

from datetime import datetime
from typing import List, Tuple
import pandas as pd

from domain.value_objects.sentiment import Sentiment
from use_cases.ports.analysis_repository import IAnalysisRepository


class UpdateSentimentUseCase:
    """
    Caso de uso que maneja la corrección manual de etiquetas de sentimiento.
    
    Permite a los ejecutivos corregir clasificaciones incorrectas y guarda
    el resultado como un nuevo análisis, preservando el original.
    """

    def __init__(self, analysis_repository: IAnalysisRepository):
        """
        Inicializa el caso de uso.
        
        Args:
            analysis_repository: Repositorio para persistir análisis
        """
        self._repository = analysis_repository

    def execute(
        self,
        analysis_id: str,
        original_df: pd.DataFrame,
        modifications: List[Tuple[int, str]]
    ) -> Tuple[bool, str, str]:
        """
        Actualiza las etiquetas de sentimiento y crea un nuevo análisis.
        
        Args:
            analysis_id: ID del análisis original
            original_df: DataFrame con los datos originales
            modifications: Lista de tuplas (índice, nueva_etiqueta_str)
        
        Returns:
            Tupla con (éxito, nuevo_analysis_id, mensaje)
        """
        # Validar que hay modificaciones
        if not modifications:
            return False, "", "No se proporcionaron modificaciones."

        # Validar que el DataFrame tiene la columna de clasificación
        if 'Clasificacion' not in original_df.columns:
            return False, "", "El DataFrame no tiene la columna 'Clasificacion'."

        # Crear copia del DataFrame para modificar
        modified_df = original_df.copy()

        # Aplicar las modificaciones y validar las etiquetas
        try:
            for index, new_label in modifications:
                # Validar que el índice existe
                if index not in modified_df.index:
                    return False, "", f"Índice {index} no existe en el DataFrame."
                
                # Validar que la nueva etiqueta es válida
                try:
                    Sentiment.from_string(new_label)
                except ValueError as e:
                    return False, "", f"Etiqueta inválida '{new_label}': {str(e)}"
                
                # Aplicar la modificación
                modified_df.at[index, 'Clasificacion'] = new_label

        except Exception as e:
            return False, "", f"Error al aplicar modificaciones: {str(e)}"

        # Generar sufijo con fecha actual (reemplazar guiones por guiones bajos)
        today = datetime.now().strftime("%Y_%m_%d")  # Cambiado de %Y-%m-%d a %Y_%m_%d
        suffix = f"_modificacion_{today}"

        # Persistir el nuevo análisis usando el repositorio
        success, new_id, message = self._repository.clone_with_modifications(
            original_analysis_id=analysis_id,
            modified_data=modified_df,
            suffix=suffix
        )

        return success, new_id, message
