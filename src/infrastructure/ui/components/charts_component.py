"""Componente para renderizar gráficos de análisis."""

import streamlit as st
import plotly.express as px
import pandas as pd
from typing import Dict

from domain.services.trend_calculator import (
    calculate_average_trend,
    calculate_sentiment_distribution_trend,
    calculate_trend_change
)


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

        # Renderizar evolución histórica (si hay datos temporales)
        self._render_evolution_chart(df, color_map)

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

    def _render_evolution_chart(
            self,
            df: pd.DataFrame,
            color_map: Dict[str, str]):
        """
        Renderiza gráficos de evolución histórica si existe la columna 'fecha'.

        Args:
            df: DataFrame con los datos
            color_map: Diccionario con mapeo de colores
        """
        if 'fecha' not in df.columns:
            st.info("Este análisis no contiene información de fechas.")
            return

        # Validar que se reciban varias fechas
        if len(df['fecha'].unique()) < 2:
            st.info("La selección no contiene información suficiente"
                    " para mostrar gráficos de evolución histórica.")
            st.info("Por favor, seleccione una fecha inicial y una fecha final"
                    " de más de un mes para mostrar gráficos de evolución"
                    " histórica.")
            return

        try:
            st.markdown("---")
            st.header("Evolución Histórica")

            # Selector de agrupación
            col_ctrl, _ = st.columns([1, 3])
            with col_ctrl:
                agrupacion = st.selectbox(
                    "Agrupación Temporal",
                    ["Mensual", "Trimestral"],
                    index=0
                )

            # Definir frecuencia para pandas grouper
            freq = 'M' if agrupacion == "Mensual" else 'Q'

            # 1. Evolución del Promedio de Calificación
            st.subheader("Evolución del Puntaje Promedio")

            df_trend = calculate_average_trend(df, freq)

            if df_trend.empty:
                st.info("No hay suficientes datos para mostrar tendencias.")
            else:
                # Calcular métricas de cambio
                last_val, _, delta = calculate_trend_change(df_trend)

                if last_val is not None and delta is not None:
                    col_metric1, _ = st.columns(2)
                    with col_metric1:
                        date_label = df_trend.iloc[-1]['fecha']\
                            .strftime('%Y-%m')
                        st.metric(
                            label=f"Promedio Actual ({date_label})",
                            value=f"{last_val:.2f}",
                            delta=f"{delta:.2f}"
                        )

                # Gráfico de línea para promedio
                fig_line = px.line(
                    df_trend,
                    x='fecha',
                    y='calificacion',
                    markers=True,
                    title=f'Promedio de Calificación ({agrupacion})',
                    labels={'calificacion': 'Puntaje Promedio',
                            'fecha': 'Fecha'}
                )
                fig_line.update_yaxes(range=[0, 10])  # Asumiendo escala 1-10
                st.plotly_chart(fig_line, use_container_width=True)

            # 2. Evolución de la Distribución de Clasificaciones
            st.subheader("Evolución de la Distribución de Sentimientos")

            df_dist = calculate_sentiment_distribution_trend(df, freq)

            if not df_dist.empty:
                fig_area = px.area(
                    df_dist,
                    x='fecha',
                    y='porcentaje',
                    color='Clasificacion',
                    title=f'Distribución de Sentimientos ({agrupacion})',
                    labels={'porcentaje': 'Porcentaje (%)', 'fecha': 'Fecha'},
                    color_discrete_map=color_map
                )
                st.plotly_chart(fig_area, use_container_width=True)

        except Exception as e:
            st.error(f"Error al renderizar gráfico de evolución: {e}")
