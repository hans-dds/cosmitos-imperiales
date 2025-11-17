"""Componente principal que maneja el contenido de la página principal."""

import pandas as pd
import streamlit as st
from typing import Optional

from infrastructure.ui.controllers.streamlit_controller import StreamlitController
from infrastructure.ui.components.analysis_state_manager import AnalysisStateManager
from infrastructure.ui.components.charts_component import ChartsComponent
from infrastructure.ui.components.table_component import TableComponent
from infrastructure.ui.components.export_component import ExportComponent


class MainContent:
    """
    Componente principal que orquesta la visualización y manejo de análisis.
    """

    def __init__(self, controller: StreamlitController):
        """
        Inicializa el componente principal.

        Args:
            controller: Controlador de Streamlit para interactuar con casos de uso
        """
        self._controller = controller
        self._state_manager = AnalysisStateManager()
        self._charts = ChartsComponent()
        self._table = TableComponent()
        self._export = ExportComponent()

    def render(
        self,
        uploaded_file,
        analysis_to_load: Optional[str]
    ):
        """
        Renderiza el contenido principal de la página.

        Args:
            uploaded_file: Archivo subido por el usuario (si hay)
            analysis_to_load: Nombre del análisis a cargar (si hay)
        """
        # Inicializar estado
        self._state_manager.initialize_state()

        # Procesar archivo subido
        if uploaded_file:
            self._handle_file_upload(uploaded_file)

        # Cargar análisis guardado si es necesario
        if self._state_manager.needs_load(analysis_to_load):
            self._handle_load_analysis(analysis_to_load)

        # Mostrar contenido del análisis actual
        self._render_analysis_display()

    def _handle_file_upload(self, uploaded_file):
        """
        Maneja la carga y procesamiento de un archivo.

        Args:
            uploaded_file: Archivo subido por el usuario
        """
        file_id = f"{uploaded_file.name}_{uploaded_file.size}"

        # Verificar si este archivo ya fue procesado
        if self._state_manager.is_file_already_processed(file_id):
            return

        file_basename = uploaded_file.name.split('.')[0]

        with st.spinner("Procesando archivo... Esto puede tardar unos segundos."):
            success, analyzed_df, error_message = self._controller.handle_file_upload(
                uploaded_file,
                file_basename
            )

        if success and analyzed_df is not None:
            new_analysis_name = f"analisis_{file_basename}"

            st.success(
                f"Archivo '{uploaded_file.name}' procesado y guardado exitosamente."
            )

            # Establecer el nuevo análisis
            self._state_manager.set_new_analysis(
                new_analysis_name,
                analyzed_df,
                file_id
            )

            # Limpiar selecciones de eliminación
            self._state_manager.clear_delete_selection()

            # Forzar actualización
            st.rerun()
        else:
            st.error(f"Ocurrió un error al procesar el archivo: {error_message}")
            self._state_manager.clear_processed_file_flag()

    def _handle_load_analysis(self, analysis_to_load: Optional[str]):
        """
        Maneja la carga de un análisis guardado.

        Args:
            analysis_to_load: Nombre del análisis a cargar
        """
        selected_analysis = st.session_state.get('selected_analysis')
        analysis_name = analysis_to_load or selected_analysis

        if not analysis_name:
            return

        success, loaded_df, error_message = self._controller.handle_load_analysis(
            analysis_name
        )

        if success and loaded_df is not None:
            self._state_manager.set_loaded_analysis(analysis_name, loaded_df)
        else:
            if error_message:
                st.warning(error_message)
            self._state_manager.clear_analysis_display()

    def _render_analysis_display(self):
        """Renderiza la visualización del análisis actual."""
        df_to_show = self._state_manager.get_current_analysis()
        analysis_name = self._state_manager.get_current_analysis_name()

        if df_to_show is None or df_to_show.empty:
            return

        # Mostrar encabezado
        st.header(analysis_name)

        # Preparar DataFrame para visualización
        if 'comentarios' in df_to_show.columns and 'longitud' not in df_to_show.columns:
            df_to_show['longitud'] = df_to_show['comentarios'].str.len()

        # Definir mapa de colores
        color_map = {
            'Promotor': '#00CC96',
            'Detractor': '#EF553B',
            'Neutro': '#636EFA'
        }

        # Renderizar componentes
        self._charts.render(df_to_show, color_map)
        self._table.render(df_to_show)
        self._export.render(df_to_show, analysis_name)

