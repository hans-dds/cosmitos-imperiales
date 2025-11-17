from abc import ABC, abstractmethod
from typing import List
from domain.entities.suggestion import Suggestion

class ISuggestionGenerator(ABC):
    """
    Puerto (Interfaz) para un servicio que genera sugerencias de mejora
    a partir de una lista de comentarios.
    """

    @abstractmethod
    def generate_suggestions(self, comments: List[str]) -> List[Suggestion]:
        """
        Toma una lista de comentarios y devuelve una lista de sugerencias.

        Args:
            comments: Una lista de comentarios de texto.

        Returns:
            Una lista de entidades Suggestion.
        """
        pass
