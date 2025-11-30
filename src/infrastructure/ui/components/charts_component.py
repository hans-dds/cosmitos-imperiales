"""Componente para renderizar gráficos de análisis."""

import streamlit as st
import plotly.express as px
import pandas as pd
from typing import Dict


class ChartsComponent:
    """Componente responsable de renderizar todos los gráficos."""

    def render(self, df: pd.DataFrame, color_map: Dict[str, str]):
        """
        Renderiza todos los gráficos para el DataFrame dado.

        Args:
            df: DataFrame con los datos a visualizar
            color_map: Diccionario con mapeo de colores por categoría
        """
        if not self._validate_data(df):
            return

        # Asegurar que existe la columna 'longitud'
        if 'longitud' not in df.columns:
            df['longitud'] = df['comentarios'].str.len()

        # Renderizar gráficos de distribución
        self._render_distribution_charts(df, color_map)

        # Renderizar histograma de longitud
        self._render_length_histogram(df, color_map)

    def _validate_data(self, df: pd.DataFrame) -> bool:
        """
        Valida que el DataFrame tenga las columnas necesarias.

        Args:
            df: DataFrame a validar

        Returns:
            True si el DataFrame es válido, False en caso contrario
        """
        if 'Clasificacion' not in df.columns or \
                'comentarios' not in df.columns:
            st.error(
                "El DataFrame no tiene las columnas requeridas para los"
                " gráficos.")
            return False
        return True

    def _render_distribution_charts(
            self,
            df: pd.DataFrame,
            color_map: Dict[str, str]):
        """
        Renderiza los gráficos de distribución (pie y bar).

        Args:
            df: DataFrame con los datos
            color_map: Diccionario con mapeo de colores
        """
        counts = df['Clasificacion'].value_counts().reset_index()
        counts.columns = ['Clasificacion', 'cantidad']

        col1, col2 = st.columns(2)

        with col1:
            self._render_pie_chart(counts, color_map)

        with col2:
            self._render_bar_chart(counts, color_map)

    def _render_pie_chart(
            self,
            counts: pd.DataFrame,
            color_map: Dict[str, str]):
        """
        Renderiza el gráfico de pastel.

        Args:
            counts: DataFrame con conteos por categoría
            color_map: Diccionario con mapeo de colores
        """
        st.subheader("Distribución de categorías")
        fig_pie = px.pie(
            counts,
            names='Clasificacion',
            values='cantidad',
            color='Clasificacion',
            color_discrete_map=color_map,
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    def _render_bar_chart(
            self,
            counts: pd.DataFrame,
            color_map: Dict[str, str]):
        """
        Renderiza el gráfico de barras.

        Args:
            counts: DataFrame con conteos por categoría
            color_map: Diccionario con mapeo de colores
        """
        st.subheader("Comentarios por Categoría")
        fig_bar = px.bar(
            counts,
            x='Clasificacion',
            y='cantidad',
            color='Clasificacion',
            text='cantidad',
            color_discrete_map=color_map
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    def _render_length_histogram(
        self,
        df: pd.DataFrame,
        color_map: Dict[str, str]
    ):
        """
        Renderiza el histograma de longitud de comentarios.

        Args:
            df: DataFrame con los datos
            color_map: Diccionario con mapeo de colores
        """
        st.subheader("¿Quiénes opinan más?")
        fig_hist = px.histogram(
            df,
            x='longitud',
            color='Clasificacion',
            nbins=15,
            barmode='overlay',
            opacity=0.8,
            title='Distribución de longitud de comentarios por categoría',
            labels={'longitud': 'Número de caracteres'},
            color_discrete_map=color_map
        )
        fig_hist.update_layout(margin=dict(t=30, b=30, l=10, r=10))
        st.plotly_chart(fig_hist, use_container_width=True)
