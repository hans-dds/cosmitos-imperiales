"""
Componente para manejar la carga de archivos en el sidebar.
"""

import streamlit as st
from typing import Optional


class FileUploadComponent:
    """
    Componente que maneja la UI y lógica de carga de archivos.
    """

    def render(self) -> Optional[object]:
        """
        Renderiza el componente de carga de archivos.
        Returns:
            Archivo subido o None si no hay archivo
        """
        st.sidebar.header("📁 Cargar y Analizar Archivo")
        uploaded_file = st.sidebar.file_uploader(
            "Sube un archivo CSV o Excel",
            type=["csv", "xlsx"]
        )
        # Si se sube un nuevo archivo (diferente al último procesado),
        # limpiar la selección
        if uploaded_file:
            file_id = f"{uploaded_file.name}_{uploaded_file.size}"
            # Solo limpiar si es un archivo nuevo, no si ya fue procesado
            if 'last_processed_file' not in st.session_state or \
                    st.session_state.last_processed_file != file_id:
                st.session_state.selected_analysis = None
        return uploaded_file
