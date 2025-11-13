from enum import Enum


class Sentiment(Enum):
    """
    Representa las posibles clasificaciones de sentimiento para una reseña.
    """
    POSITIVE = "Positivo"
    NEGATIVE = "Negativo"
    NEUTRAL = "Neutro"

    @classmethod
    def from_string(cls, value: str):
        """
        Crea un miembro de Sentiment a partir de su representación en cadena.
        """
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        raise ValueError(f"'{value}' no es una cadena de sentimiento válida.")
