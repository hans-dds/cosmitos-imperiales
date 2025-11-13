import streamlit as st
from typing import Tuple, Optional
from use_cases.list_analyses_use_case import ListAnalysesUseCase


def show_sidebar(list_analyses_use_case: ListAnalysesUseCase) \
        -> Tuple[Optional[object], Optional[str]]:
    """
    Renderiza la interfaz de usuario de la barra lateral, incluyendo el
    cargador de archivos y la lista de análisis guardados.

    Args:
        list_analyses_use_case: El caso de uso para listar análisis guardados.

    Returns:
        Una tupla que contiene el objeto de archivo cargado y el nombre del
        análisis a cargar, o None para cualquiera si no aplica.
    """
    st.sidebar.title("Controles")
    analysis_to_load = None

    # --- Cargador de Archivos ---
    st.sidebar.header("📁 Cargar y Analizar Archivo")
    uploaded_file = st.sidebar.file_uploader(
        "Sube un archivo CSV o Excel", type=["csv", "xlsx"])

    # --- Análisis Guardados ---
    st.sidebar.header("📂 Ver Análisis Guardado")
    saved_analyses = list_analyses_use_case.execute()
    if not saved_analyses:
        st.sidebar.info("No hay análisis guardados en la base de datos.")
    else:
        selected_analysis = st.sidebar.selectbox(
            "Seleccionar análisis", saved_analyses)
        if st.sidebar.button("Cargar Análisis"):
            analysis_to_load = selected_analysis

    return uploaded_file, analysis_to_load
