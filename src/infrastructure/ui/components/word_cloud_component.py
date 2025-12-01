"""
Componente para renderizar nube de palabras.
"""

import streamlit as st
import pandas as pd
from wordcloud import WordCloud

from domain.services.word_cloud_service import build_corpus, get_stopwords


class WordCloudComponent:
    """
    Componente responsable de renderizar la nube de palabras.
    """
    
    def render(self, df: pd.DataFrame, max_words: int = 120):
        """
        Renderiza una nube de palabras para los comentarios del DataFrame.
        
        Args:
            df: DataFrame con los datos a visualizar (debe contener columna 'comentarios')
            max_words: Número máximo de palabras a mostrar en la nube
        """
        if not self._validate_data(df):
            return
        
        comentarios = df["comentarios"].dropna().tolist()
        
        if not comentarios:
            st.info("No hay comentarios disponibles para generar la nube de palabras.")
            return
        
        # Construir corpus usando el servicio de dominio
        corpus = build_corpus(comentarios)
        
        if not corpus:
            st.info(
                "Los comentarios disponibles no contienen suficiente texto para generar la nube."
            )
            return
        
        # Generar nube de palabras
        word_cloud = self._generate_word_cloud(corpus, max_words)
        
        # Renderizar
        self._render_word_cloud(word_cloud)
    
    def _validate_data(self, df: pd.DataFrame) -> bool:
        """
        Valida que el DataFrame tenga la columna necesaria.
        
        Args:
            df: DataFrame a validar
            
        Returns:
            True si el DataFrame es válido, False en caso contrario
        """
        if "comentarios" not in df.columns:
            st.info("No se encontró la columna 'comentarios' para generar la nube.")
            return False
        return True
    
    def _generate_word_cloud(self, corpus: str, max_words: int) -> WordCloud:
        """
        Genera el objeto WordCloud a partir del corpus.
        
        Args:
            corpus: Texto procesado para la nube
            max_words: Número máximo de palabras
            
        Returns:
            Objeto WordCloud generado
        """
        stopwords = get_stopwords()
        
        return WordCloud(
            width=900,
            height=400,
            background_color="white",
            colormap="viridis",
            max_words=max_words,
            stopwords=stopwords,
        ).generate(corpus)
    
    def _render_word_cloud(self, word_cloud: WordCloud):
        """
        Renderiza la nube de palabras en Streamlit.
        
        Args:
            word_cloud: Objeto WordCloud a renderizar
        """
        st.subheader("Nube de palabras")
        st.image(word_cloud.to_array(), use_container_width=True)
        st.caption(
            "Las palabras con mayor tamaño aparecen con mayor frecuencia en los comentarios analizados."
        )

