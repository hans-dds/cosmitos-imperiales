from dataclasses import dataclass

from domain.value_objects.sentiment import Sentiment


@dataclass(frozen=True)
class Review:
    """
    Representa una única reseña de cliente antes del análisis.
    """
    comment: str
    rating: int


@dataclass(frozen=True)
class AnalyzedReview(Review):
    """
    Representa una reseña después de haber sido analizada y clasificada.
    """
    sentiment: Sentiment
