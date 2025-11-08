import re
import string
import unicodedata
import numpy as np
from typing import List, Union

# Regla de negocio central sobre comentarios que no queremos.
IRRELEVANT_PATTERNS: List[str] = [
    r'^solo califica',
    r'^no (?:brinda|proporciona|quiso|tiene|contesta)',
    r'^sin comentarios?$',
    r'^ningun[ao]s?$',
    r'^\d+cm$',
    r'^se envia whatsapp$',
    r'^(?:bdc|ok|na|s c)$'
]

def clean_text(text: str) -> Union[str, float]:
    """
    Aplica todas las reglas de limpieza de texto del dominio 
    a una sola cadena.
    """
    if not isinstance(text, str) or text.strip() == '':
        return np.nan

    # 1. Convertir a minúsculas
    clean_text = text.lower()
    
    # 2. Eliminar acentos
    nfkd_form = unicodedata.normalize('NFD', clean_text)
    clean_text = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    
    # 3. Eliminar signos de puntuación
    clean_text = re.sub(f'[{re.escape(string.punctuation)}]', ' ', clean_text)
    
    # 4. Eliminar saltos de línea y espacios extra
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    return clean_text if clean_text else np.nan

def is_comment_relevant(clean_text: str) -> bool:
    """
    Verifica si un comentario (YA LIMPIO) es relevante según
    las reglas de negocio.
    """
    if not clean_text or len(clean_text) < 5:
        return False
    
    # Filtro regex a partir de las reglas de negocio
    regex_filter = '|'.join(IRRELEVANT_PATTERNS)
    if re.search(regex_filter, clean_text):
        return False
        
    return True