"""Componente para renderizar tablas de comentarios."""

import streamlit as st
import pandas as pd


class TableComponent:
    """Componente responsable de renderizar la tabla de comentarios."""

    REQUIRED_COLUMNS = ['calificacion', 'comentarios', 'Clasificacion']
    DISPLAY_COLUMNS = ['calificacion',
                       'comentarios', 'Clasificacion', 'Fiabilidad']

    def render(self, df: pd.DataFrame):
        """
        Renderiza la tabla de comentarios con filtros.

        Args:
            df: DataFrame con los datos a mostrar
        """
        if not self._validate_columns(df):
            return

        st.subheader("Comentarios Filtrados")

        # Crear copia con las columnas a mostrar (incluyendo Fiabilidad
        # si existe)
        columns_to_display = [
            col for col in self.DISPLAY_COLUMNS
            if col in df.columns
        ]
        display_df = df[columns_to_display].copy()

        # Aplicar filtros
        display_df = self._apply_filters(display_df)

        # Mostrar tabla
        self._render_table(display_df)

    def _validate_columns(self, df: pd.DataFrame) -> bool:
        """
        Valida que el DataFrame tenga las columnas requeridas.

        Args:
            df: DataFrame a validar

        Returns:
            True si tiene las columnas requeridas, False en caso contrario
        """
        missing_columns = [
            col for col in self.REQUIRED_COLUMNS
            if col not in df.columns
        ]

        if missing_columns:
            st.warning(
                f"No hay datos completos para mostrar. "
                f"Faltan las columnas: {', '.join(missing_columns)}"
            )
            return False
        # Si no existe Fiabilidad, agregarla con valor por defecto
        if 'Fiabilidad' not in df.columns:
            df['Fiabilidad'] = 'N/A'

        return True

    def _apply_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica filtros a la tabla.

        Args:
            df: DataFrame a filtrar

        Returns:
            DataFrame filtrado
        """
        # Filtro por categoría
        categories = ['Todas'] + sorted(
            df['Clasificacion'].dropna().unique().tolist()
        )
        selected_category = st.selectbox("Filtrar por categoría", categories)
        # Persistir selección para sincronizar con exportación a PDF
        st.session_state["comments_filter_category"] = selected_category

        if selected_category != 'Todas':
            df = df[df['Clasificacion'] == selected_category]

        return df

    def _render_table(self, df: pd.DataFrame):
        """
        Renderiza la tabla con controles de cantidad.

        Args:
            df: DataFrame a mostrar
        """
        # Control de cantidad de comentarios
        max_comments = max(10, len(df))
        number_of_comments = st.slider(
            "Número de comentarios a mostrar",
            min_value=10,
            max_value=max_comments,
            value=min(10, max_comments)
        )
        # Persistir cantidad seleccionada para exportación a PDF
        st.session_state["comments_filter_count"] = int(number_of_comments)
        # Preparar nombres de columnas para mostrar
        column_mapping = {
            'calificacion': 'Calificación',
            'comentarios': 'Comentario',
            'Clasificacion': 'Clasificación',
            'Fiabilidad': 'Fiabilidad'
        }
        # Renombrar columnas para mostrar
        display_df_renamed = df.rename(columns=column_mapping)
        # Mostrar tabla
        st.dataframe(
            display_df_renamed.head(number_of_comments),
            use_container_width=True,
            hide_index=True
        )
