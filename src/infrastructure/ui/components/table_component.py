"""Componente para renderizar tablas de comentarios."""

import streamlit as st
import pandas as pd


class TableComponent:
    """Componente responsable de renderizar la tabla de comentarios."""

    REQUIRED_COLUMNS = ["calificacion", "comentarios", "Clasificacion"]
    DISPLAY_COLUMNS = [
        "calificacion",
        "comentarios",
        "Clasificacion",
        "Fiabilidad",
    ]

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
            col for col in self.DISPLAY_COLUMNS if col in df.columns
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
            col for col in self.REQUIRED_COLUMNS if col not in df.columns
        ]

        if missing_columns:
            st.warning(
                f"No hay datos completos para mostrar. "
                f"Faltan las columnas: {', '.join(missing_columns)}"
            )
            return False
        # Si no existe Fiabilidad, agregarla con valor por defecto
        if "Fiabilidad" not in df.columns:
            df["Fiabilidad"] = "N/A"

        return True

    def _apply_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica filtros a la tabla.

        Args:
            df: DataFrame a filtrar

        Returns:
            DataFrame filtrado
        """
        # Preparar opciones de filtros y orden
        categories = ["Todas"] + sorted(
            df["Clasificacion"].dropna().unique().tolist()
        )
        prev_category = st.session_state.get(
            "comments_filter_category", "Todas"
        )
        category_index = (
            categories.index(prev_category)
            if prev_category in categories
            else 0
        )

        sort_options = ["Sin ordenar", "Calificación", "Clasificación"]
        if "Fiabilidad" in df.columns:
            sort_options.append("Fiabilidad")
        prev_sort = st.session_state.get("comments_sort_by", "Sin ordenar")
        sort_index = (
            sort_options.index(prev_sort) if prev_sort in sort_options else 0
        )

        sort_dir_options = ["Ascendente", "Descendente"]
        prev_dir = st.session_state.get("comments_sort_dir", "Descendente")
        dir_index = (
            sort_dir_options.index(prev_dir)
            if prev_dir in sort_dir_options
            else 1
        )

        # Mostrar controles en una sola línea usando columnas
        col1, col2, col3 = st.columns([3, 3, 2])
        with col1:
            selected_category = st.selectbox(
                "Filtrar por categoría",
                categories,
                index=category_index,
            )
            st.session_state["comments_filter_category"] = selected_category
        # Filtrar según la categoría seleccionada
        if selected_category != "Todas":
            df = df[df["Clasificacion"] == selected_category]

        with col2:
            sort_by_label = st.selectbox(
                "Ordenar por",
                options=sort_options,
                index=sort_index,
            )
            st.session_state["comments_sort_by"] = sort_by_label

        with col3:
            sort_dir_label = st.radio(
                "Dirección",
                options=sort_dir_options,
                horizontal=True,
                index=dir_index,
            )
            st.session_state["comments_sort_dir"] = sort_dir_label

        # Aplicar orden si corresponde
        label_to_column = {
            "Calificación": "calificacion",
            "Clasificación": "Clasificacion",
            "Fiabilidad": "Fiabilidad",
        }
        if sort_by_label != "Sin ordenar":
            col = label_to_column.get(sort_by_label)
            if col in df.columns:
                df = df.sort_values(
                    by=col,
                    ascending=(sort_dir_label == "Ascendente"),
                    kind="mergesort",
                )

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
            value=min(10, max_comments),
        )
        # Persistir cantidad seleccionada para exportación a PDF
        st.session_state["comments_filter_count"] = int(number_of_comments)
        # Preparar nombres de columnas para mostrar
        column_mapping = {
            "calificacion": "Calificación",
            "comentarios": "Comentario",
            "Clasificacion": "Clasificación",
            "Fiabilidad": "Fiabilidad",
        }
        # Renombrar columnas para mostrar
        display_df_renamed = df.rename(columns=column_mapping)
        # Mostrar tabla
        st.dataframe(
            display_df_renamed.head(number_of_comments),
            use_container_width=True,
            hide_index=True,
        )

    def render_editable(self, df: pd.DataFrame) -> tuple[pd.DataFrame, bool]:
        """
        Renderiza la tabla con capacidad de edición de etiquetas y detecta cambios.

        Args:
            df: DataFrame con los datos a mostrar

        Returns:
            Tupla con (DataFrame editado, hay_cambios_pendientes)
        """
        if not self._validate_columns(df):
            return df, False

        st.subheader("Comentarios Filtrados")

        # Crear copia con las columnas a mostrar
        columns_to_display = [
            col for col in self.DISPLAY_COLUMNS if col in df.columns
        ]
        display_df = df[columns_to_display].copy()

        # Aplicar filtros
        display_df = self._apply_filters(display_df)

        # Renderizar tabla editable
        edited_df, has_changes = self._render_editable_table(display_df)

        return edited_df, has_changes

    def _render_editable_table(
        self, df: pd.DataFrame
    ) -> tuple[pd.DataFrame, bool]:
        """
        Renderiza la tabla editable con dropdown para clasificación.

        Args:
            df: DataFrame a mostrar y editar

        Returns:
            Tupla con (DataFrame editado, hay_cambios_pendientes)
        """
        # Control de cantidad de comentarios
        max_comments = max(10, len(df))
        number_of_comments = st.slider(
            "Número de comentarios a mostrar",
            min_value=10,
            max_value=max_comments,
            value=min(10, max_comments),
        )
        st.session_state["comments_filter_count"] = int(number_of_comments)

        # Preparar DataFrame para edición
        df_to_edit = df.head(number_of_comments).copy()

        # Preparar nombres de columnas para mostrar
        column_mapping = {
            "calificacion": "Calificación",
            "comentarios": "Comentario",
            "Clasificacion": "Clasificación",
            "Fiabilidad": "Fiabilidad",
        }

        # Renombrar columnas para mostrar
        df_renamed = df_to_edit.rename(columns=column_mapping)

        # Guardar o resetear estado original cuando cambia el contenido mostrado
        prev_original = st.session_state.get("original_df_for_edit")
        if (
            prev_original is None
            or prev_original.shape != df_renamed.shape
            or not prev_original.equals(df_renamed)
        ):
            st.session_state["original_df_for_edit"] = df_renamed.copy()

        # Configurar columna editable con dropdown
        column_config = {
            "Clasificación": st.column_config.SelectboxColumn(
                "Clasificación",
                help="Selecciona la clasificación correcta",
                options=["Detractor", "Neutro", "Promotor"],
                required=True,
            )
        }

        # Renderizar tabla editable
        edited_df = st.data_editor(
            df_renamed,
            use_container_width=True,
            hide_index=True,
            column_config=column_config,
            disabled=["Calificación", "Comentario", "Fiabilidad"],
            key="editable_comments_table",
        )

        # Detectar cambios comparando con el original
        has_changes = False
        if (
            "Clasificación" in edited_df.columns
            and "Clasificación"
            in st.session_state["original_df_for_edit"].columns
        ):
            original_classifications = st.session_state[
                "original_df_for_edit"
            ]["Clasificación"].values
            current_classifications = edited_df["Clasificación"].values

            # Si las longitudes difieren, hay cambios (p.ej. cambió el slider)
            if len(original_classifications) != len(current_classifications):
                has_changes = True
            else:
                # Comparar de forma segura cuando las longitudes coinciden
                has_changes = not (
                    original_classifications == current_classifications
                ).all()

        return edited_df, has_changes
