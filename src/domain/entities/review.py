from typing import Optional
# 1. Importa tus nuevas excepciones y tu Objeto de Valor
from ..exceptions.exceptions import InvalidReviewError, InvalidClassificationError
from ..value_objects.sentiment import SentimentCategory

class Review:
    def __init__(self, texto: str, calificacion: Optional[int] = None):
        if not isinstance(texto, str) or not texto.strip():
            raise InvalidReviewError("El texto de la opinión no puede estar vacío.")
        if calificacion is not None and (not isinstance(calificacion, int) or not (0 <= calificacion <= 10)):
            raise InvalidReviewError(f"La calificación '{calificacion}' debe ser un entero entre 0 y 10.")
        
        self.texto = texto
        self.calificacion = calificacion

    def __repr__(self):
        return f"Review(texto='{self.texto[:30]}...', calif={self.calificacion})"

    def to_dict(self):
        return {
            "comentarios": self.texto,
            "calificacion": self.calificacion,
        }

class ClasificatedReview(Review):
    def __init__(self, 
                 texto: str, 
                 calificacion: Optional[int] = None, 
                 clasificacion: Optional[SentimentCategory] = None):
        
        super().__init__(texto, calificacion)
        
        if not isinstance(clasificacion, SentimentCategory):
            raise InvalidClassificationError(f"La clasificación '{clasificacion}' no es un objeto SentimentCategory válido.")
            
        self.clasificacion = clasificacion
        self.longitud = len(texto)

    def __repr__(self):
        return (f"ClasificatedReview(texto='{self.texto[:30]}...', "
                f"calif={self.calificacion}, clasif='{self.clasificacion.value}')")

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict["clasificacion"] = self.clasificacion.value
        base_dict["longitud"] = self.longitud
        return base_dict