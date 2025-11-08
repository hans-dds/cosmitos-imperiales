from enum import Enum

class SentimentCategory(Enum):
    """
    Objeto de Valor que representa las únicas clasificaciones permitidas en el dominio.
    """
    PROMOTER = "Promotor"
    NEUTRAL = "Neutro"
    DETRACTOR = "Detractor"