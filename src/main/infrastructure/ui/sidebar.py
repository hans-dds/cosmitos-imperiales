import streamlit as st
from typing import Tuple, Optional
from use_cases.list_analyses_use_case import ListAnalysesUseCase


def show_sidebar(list_analyses_use_case: ListAnalysesUseCase) \
        -> Tuple[Optional[object], Optional[str]]:
    """
    Renders the sidebar UI, including the file uploader and the list of
    saved analyses.

    Args:
        list_analyses_use_case: The use case for listing saved analyses.

    Returns:
        A tuple containing the uploaded file object and the name of the
        analysis to load, or None for either if not applicable.
    """
    st.sidebar.title("Controles")
    analysis_to_load = None

    # --- File Uploader ---
    st.sidebar.header("📁 Cargar y Analizar Archivo")
    uploaded_file = st.sidebar.file_uploader(
        "Sube un archivo CSV o Excel", type=["csv", "xlsx"])

    # --- Saved Analyses ---
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
