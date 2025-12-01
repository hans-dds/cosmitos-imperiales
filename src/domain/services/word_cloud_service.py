"""
Servicio de dominio para procesar texto y generar nubes de palabras.

Este módulo encapsula la lógica de procesamiento de texto para nubes de palabras,
incluyendo normalización, stopwords y generación del corpus.
"""

import re
import unicodedata
from typing import Iterable, Set
from wordcloud import STOPWORDS


def get_custom_stopwords() -> Set[str]:
    """
    Retorna un conjunto de stopwords personalizadas en español.
    
    Estas son palabras comunes que no aportan información significativa
    para el análisis de sentimientos y deben ser filtradas.
    
    Returns:
        Conjunto de stopwords personalizadas
    """
    return {
        "cliente",
        "clientes",
        "tienda",
        "producto",
        "productos",
        "servicio",
        "servicios",
        "muchas",
        "gracias",
        "favor",
        "poder",
        "puede",
        "pueden",
        "cuando",
        "donde",
        "desde",
        "sobre",
        "tambien",
        "asi",
        "todos",
        "todas",
        "solo",
        "aqui",
        "all",
        "aun",
        "mas",
        "menos",
        "muy",
        "la",
        "el",
        "que",
        "fue",
        "de",
        "en",
        "un",
        "lo",
        "una",
        "se",
        "si",
        "por",
        "parte",
        "dan",
        "pero",
        "o",
        "mi",
        "las",
        "esta",
        "los",
        "y",
        "ya",
        "te",
        "sin",
        "su",
        "es",
        "al",
        "ha",
        "tuvo",
        "son",
        "le",
        "demasiado",
        "sido",
        "bastante",
        "para",
        "tu",
        "ni",
        "tiene",
        "hubo",
        "sus",
        "con",
        "5cm",
        "del",
        "vehiculo"
    }


def normalize_comment(comment: str) -> str:
    """
    Normaliza un comentario: convierte a minúsculas, elimina acentos
    y mantiene solo caracteres alfanuméricos.
    
    Esta normalización permite que las stopwords permanezcan en ASCII
    y facilita el procesamiento del texto.
    
    Args:
        comment: Comentario a normalizar
        
    Returns:
        Comentario normalizado
    """
    text = unicodedata.normalize("NFKD", str(comment)).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def build_corpus(comments: Iterable[str]) -> str:
    """
    Construye un corpus de texto a partir de una colección de comentarios.
    
    Normaliza todos los comentarios y los une en un solo texto.
    
    Args:
        comments: Iterable de comentarios
        
    Returns:
        Corpus de texto normalizado
    """
    normalized = [normalize_comment(comment) for comment in comments]
    normalized = [comment for comment in normalized if comment]
    return " ".join(normalized)


def get_stopwords() -> Set[str]:
    """
    Retorna el conjunto completo de stopwords (estándar + personalizadas).
    
    Returns:
        Conjunto de stopwords para filtrar palabras comunes
    """
    return STOPWORDS.union(get_custom_stopwords())

