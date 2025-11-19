"""Módulo para gestionar el estado de los análisis en Streamlit."""

import streamlit as st
from typing import Optional
import pandas as pd


class AnalysisStateManager:
    """
    Gestiona el estado de los análisis en la sesión de Streamlit.
    """

    @staticmethod
    def initialize_state():
        """Inicializa los estados necesarios en session_state."""
        if 'selected_analysis' not in st.session_state:
            st.session_state.selected_analysis = None
        if 'last_loaded_analysis' not in st.session_state:
            st.session_state.last_loaded_analysis = None
        if 'analysis_name' not in st.session_state:
            st.session_state.analysis_name = None
        if 'analyses_to_delete' not in st.session_state:
            st.session_state.analyses_to_delete = []
        if 'confirm_delete' not in st.session_state:
            st.session_state.confirm_delete = False

    @staticmethod
    def set_new_analysis(
        analysis_name: str, analyzed_df: pd.DataFrame, file_id: str
    ):
        """
        Establece un nuevo análisis como el actual.

        Args:
            analysis_name: Nombre del análisis
            analyzed_df: DataFrame con los datos analizados
            file_id: Identificador único del archivo procesado
        """
        st.session_state.selected_analysis = analysis_name
        st.session_state.last_loaded_analysis = analysis_name
        st.session_state.df_display = analyzed_df
        st.session_state.analysis_name = analysis_name
        st.session_state.last_processed_file = file_id

    @staticmethod
    def set_loaded_analysis(analysis_name: str, loaded_df: pd.DataFrame):
        """
        Establece un análisis cargado como el actual.

        Args:
            analysis_name: Nombre del análisis
            loaded_df: DataFrame con los datos cargados
        """
        st.session_state.df_display = loaded_df
        st.session_state.analysis_name = analysis_name
        st.session_state.last_loaded_analysis = analysis_name

    @staticmethod
    def clear_analysis_display():
        """Limpia los datos de análisis del estado."""
        if 'df_display' in st.session_state:
            del st.session_state.df_display

    @staticmethod
    def clear_delete_selection():
        """Limpia la selección de análisis para eliminar."""
        if 'analyses_to_delete' in st.session_state:
            st.session_state.analyses_to_delete = []
        if 'confirm_delete' in st.session_state:
            st.session_state.confirm_delete = False

    @staticmethod
    def get_current_analysis() -> Optional[pd.DataFrame]:
        """
        Obtiene el DataFrame del análisis actual.

        Returns:
            DataFrame del análisis actual o None si no hay ninguno cargado
        """
        return st.session_state.get('df_display')

    @staticmethod
    def get_current_analysis_name() -> Optional[str]:
        """
        Obtiene el nombre del análisis actual.

        Returns:
            Nombre del análisis actual o None
        """
        return st.session_state.get('analysis_name')

    @staticmethod
    def needs_load(analysis_to_load: Optional[str]) -> bool:
        """
        Determina si se necesita cargar un análisis.

        Args:
            analysis_to_load: Nombre del análisis a cargar
            (si hay uno explícito)

        Returns:
            True si se necesita cargar un análisis, False en caso contrario
        """
        selected_analysis = st.session_state.get('selected_analysis')
        current_analysis_name = st.session_state.get('analysis_name')

        if analysis_to_load:
            return True
        elif selected_analysis and \
                selected_analysis != st.session_state.get(
                    'last_loaded_analysis'):
            if current_analysis_name != selected_analysis:
                return True
        return False

    @staticmethod
    def is_file_already_processed(file_id: str) -> bool:
        """
        Verifica si un archivo ya fue procesado en esta sesión.

        Args:
            file_id: Identificador único del archivo

        Returns:
            True si el archivo ya fue procesado, False en caso contrario
        """
        return (
            'last_processed_file' in st.session_state and
            st.session_state.last_processed_file == file_id
        )

    @staticmethod
    def clear_processed_file_flag():
        """Limpia el flag de archivo procesado para permitir reintentar."""
        if 'last_processed_file' in st.session_state:
            del st.session_state.last_processed_file
