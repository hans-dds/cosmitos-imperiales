from abc import ABC, abstractmethod
from typing import List, Dict


class ISuggestionGenerator(ABC):
    """
    Puerto (Interfaz) para el servicio que genera sugerencias de mejora
    basadas en comentarios.
    """

    @abstractmethod
    def generate(self, comments: List[str]) -> List[Dict[str, str]]:
        """
        Genera una lista de sugerencias basadas en una lista de comentarios negativos.

        Args:
            comments: Lista de textos (comentarios de detractores).

        Returns:
            Lista de diccionarios, donde cada uno tiene:
            - 'tema': El problema identificado.
            - 'sugerencia': La acción recomendada.
        """
        pass
