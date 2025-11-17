import re
import string
import unicodedata


def clean_text(text: str) -> str | None:
    """
    Aplica todas las reglas de limpieza a una única cadena de texto.
    - Convierte a minúsculas
    - Elimina acentos
    - Elimina puntuación
    - Elimina espacios en blanco y saltos de línea extra

    Devuelve el texto limpio o None si la entrada es inválida o está vacía.
    """
    if not isinstance(text, str) or not text.strip():
        return None

    # 1. Convertir a minúsculas
    text = text.lower()

    # 2. Eliminar acentos
    nfkd_form = unicodedata.normalize('NFD', text)
    text = "".join([c for c in nfkd_form if not unicodedata.combining(c)])

    # 3. Eliminar puntuación
    text = re.sub(f'[{re.escape(string.punctuation)}]', ' ', text)

    # 4. Eliminar saltos de línea y espacios extra
    text = re.sub(r'\s+', ' ', text).strip()

    return text if text else None
