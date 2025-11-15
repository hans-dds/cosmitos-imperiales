"""Utilities to render a word cloud for the comments dashboard."""

from __future__ import annotations

import re
import unicodedata
from typing import Iterable

import streamlit as st
from wordcloud import STOPWORDS, WordCloud

# Basic Spanish stopwords kept in ASCII by removing accents ahead of time.
_CUSTOM_STOPWORDS = {
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


def _normalize_comment(comment: str) -> str:
    """Lowercase, strip accents, and keep alphanumerics so stopwords remain ASCII."""
    text = unicodedata.normalize("NFKD", str(comment)).encode("ascii", "ignore").decode(
        "ascii"
    )
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _to_corpus(comments: Iterable[str]) -> str:
    normalized = [_normalize_comment(comment) for comment in comments]
    normalized = [comment for comment in normalized if comment]
    return " ".join(normalized)


def show_word_cloud(df, *, max_words: int = 120) -> None:
    """Render a Streamlit word cloud for the provided comments DataFrame."""
    if "comentarios" not in df.columns:
        st.info("No se encontro la columna 'comentarios' para generar la nube.")
        return

    comentarios = df["comentarios"].dropna().tolist()
    if not comentarios:
        st.info("No hay comentarios disponibles para generar la nube de palabras.")
        return

    corpus = _to_corpus(comentarios)
    if not corpus:
        st.info(
            "Los comentarios disponibles no contienen suficiente texto para generar la nube."
        )
        return

    stopwords = STOPWORDS.union(_CUSTOM_STOPWORDS)
    word_cloud = WordCloud(
        width=900,
        height=400,
        background_color="white",
        colormap="viridis",
        max_words=max_words,
        stopwords=stopwords,
    ).generate(corpus)

    st.subheader("Nube de palabras")
    st.image(word_cloud.to_array(), use_container_width=True)
    st.caption(
        "Las palabras con mayor tamano aparecen con mayor frecuencia en los comentarios analizados."
    )
