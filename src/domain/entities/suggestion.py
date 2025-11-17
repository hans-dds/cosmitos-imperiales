from dataclasses import dataclass

@dataclass(frozen=True)
class Suggestion:
    """
    Representa una sugerencia de mejora generada por el LLM.
    """
    theme: str 
    recommendation: str 
