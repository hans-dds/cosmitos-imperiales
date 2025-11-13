from enum import Enum


class Sentiment(Enum):
    """
    Represents the possible sentiment classifications for a review.
    """
    POSITIVE = "Positivo"
    NEGATIVE = "Negativo"
    NEUTRAL = "Neutro"

    @classmethod
    def from_string(cls, value: str):
        """
        Creates a Sentiment member from its string representation.
        """
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        raise ValueError(f"'{value}' is not a valid sentiment string.")
