from dataclasses import dataclass

from domain.value_objects.sentiment import Sentiment


@dataclass(frozen=True)
class Review:
    """
    Represents a single customer review before analysis.
    """
    comment: str
    rating: int


@dataclass(frozen=True)
class AnalyzedReview(Review):
    """
    Represents a review after it has been analyzed and classified.
    """
    sentiment: Sentiment
