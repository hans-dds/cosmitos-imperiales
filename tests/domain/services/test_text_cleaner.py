import pytest
from domain.services.text_cleaner import clean_text

def test_clean_text_basic():
    text = "Hola Mundo"
    assert clean_text(text) == "hola mundo"

def test_clean_text_accents():
    text = "Camión, Cigüeña"
    # ciguea? normalization NFD decomposes chars, filtering non-combining keeps base char
    # Camión -> Camion
    assert clean_text(text) == "camion ciguena"

def test_clean_text_punctuation():
    text = "Hola!!!, Que tal?"
    assert clean_text(text) == "hola que tal"

def test_clean_text_whitespace():
    text = "  Hola    Mundo  "
    assert clean_text(text) == "hola mundo"

def test_clean_text_invalid_input():
    assert clean_text(None) is None
    assert clean_text("") is None
    assert clean_text("   ") is None
    assert clean_text(123) is None

def test_clean_text_numbers():
    # Punctuation cleaning re.sub excludes only punctuation. Numbers should stay?
    # re punctuation includes characters not numbers.
    # Code: re.sub(f'[{re.escape(string.punctuation)}]', ' ', text)
    text = "Modelo 123"
    assert clean_text(text) == "modelo 123"
