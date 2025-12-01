"""Utilidades de texto para la capa UI.

Estas funciones deben ser puras y libres de efectos secundarios,
y nunca ser importadas desde el dominio.
"""
from __future__ import annotations


def to_pdf_compatible(text: str) -> str:
    """Convierte texto a una representación compatible con FPDF (latin-1).

    - Elimina caracteres fuera de latin-1 (p. ej., emojis como 👍).
    - Evita excepciones de codificación al escribir en FPDF con fuentes no Unicode.
    """
    if text is None:
        return ""
    try:
        return str(text).encode("latin-1", "ignore").decode("latin-1")
    except Exception:
        return ""


def normalize_newlines(text: str, replacement: str = " ") -> str:
    """Normaliza saltos de línea en texto, sustituyéndolos por espacios.

    - Convierte CRLF / CR a LF y luego reemplaza cada salto por `replacement`.
    - Colapsa espacios repetidos para evitar huecos excesivos.
    """
    if text is None:
        return ""
    s = str(text)
    # Unificar saltos y reemplazar por espacio (u otro separador)
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = replacement.join(s.splitlines())
    # Colapsar espacios múltiples a uno solo
    s = " ".join(s.split())
    return s
