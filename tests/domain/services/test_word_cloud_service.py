import pytest
from domain.services.word_cloud_service import (
    get_custom_stopwords, 
    normalize_comment, 
    build_corpus, 
    get_stopwords
)

def test_get_custom_stopwords():
    sw = get_custom_stopwords()
    assert isinstance(sw, set)
    assert "cliente" in sw
    assert "gracias" in sw
    assert "vehiculo" in sw

def test_normalize_comment():
    # Test basic normalization
    assert normalize_comment("HOLA") == "hola"
    # Test accents
    assert normalize_comment("camión") == "camion"
    # Test special chars
    assert normalize_comment("¡Hola! ¿Qué tal?") == "hola que tal"
    # Test whitespace
    assert normalize_comment("  hola   mundo  ") == "hola mundo"
    # Test numbers kept
    assert normalize_comment("modelo 2023") == "modelo 2023"

def test_build_corpus():
    comments = ["Hola Mundo", "  Prueba  ", ""]
    # Should filter empty, normalize others and join
    corpus = build_corpus(comments)
    assert corpus == "hola mundo prueba"

def test_get_stopwords():
    sw = get_stopwords()
    custom = get_custom_stopwords()
    assert custom.issubset(sw)
    # Check a standard stopword
    assert "the" in sw  # English stopwords are in default STOPWORDS?
    # actually wordcloud STOPWORDS are mostly english.
    # checking one from custom list is enough validation of union
    assert "cliente" in sw
