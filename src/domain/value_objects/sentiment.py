from enum import Enum


class Sentiment(Enum):
    """
    Representa las posibles clasificaciones de sentimiento para una reseña.
    Mapea los valores numéricos del modelo ML a etiquetas de texto.
    """
    DETRACTOR = "Detractor"  # -1
    NEUTRAL = "Neutro"       # 0
    PROMOTOR = "Promotor"    # 1

    @classmethod
    def from_numeric(cls, value: int) -> 'Sentiment':
        """
        Crea un miembro de Sentiment a partir de su valor numérico.
        
        Args:
            value: Valor numérico del modelo (-1, 0, o 1)
            
        Returns:
            El miembro de Sentiment correspondiente
            
        Raises:
            ValueError: Si el valor no es -1, 0, o 1
        """
        mapping = {
            -1: cls.DETRACTOR,
            0: cls.NEUTRAL,
            1: cls.PROMOTOR
        }
        if value not in mapping:
            raise ValueError(f"'{value}' no es un valor de sentimiento válido. Debe ser -1, 0, o 1.")
        return mapping[value]

    @classmethod
    def from_string(cls, value: str) -> 'Sentiment':
        """
        Crea un miembro de Sentiment a partir de su representación en cadena.
        
        Args:
            value: Cadena de texto ("Detractor", "Neutro", o "Promotor")
            
        Returns:
            El miembro de Sentiment correspondiente
            
        Raises:
            ValueError: Si el valor no es una cadena válida
        """
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        raise ValueError(f"'{value}' no es una cadena de sentimiento válida. Debe ser 'Detractor', 'Neutro', o 'Promotor'.")
