import re
import string
import unicodedata


def clean_text(text: str) -> str | None:
    """
    Applies all cleaning rules to a single string of text.
    - Converts to lowercase
    - Removes accents
    - Removes punctuation
    - Removes extra whitespace and newlines

    Returns the cleaned text or None if the input is invalid or empty.
    """
    if not isinstance(text, str) or not text.strip():
        return None

    # 1. Convert to lowercase
    text = text.lower()

    # 2. Remove accents
    nfkd_form = unicodedata.normalize('NFD', text)
    text = "".join([c for c in nfkd_form if not unicodedata.combining(c)])

    # 3. Remove punctuation
    text = re.sub(f'[{re.escape(string.punctuation)}]', ' ', text)

    # 4. Remove newlines and extra spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text if text else None
