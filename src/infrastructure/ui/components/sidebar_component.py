"""
Componente principal del sidebar que orquesta la renderización de la barra lateral.
"""

import streamlit as st
from typing import Tuple, Optional
from infrastructure.ui.controllers.streamlit_controller import StreamlitController
from infrastructure.ui.components.file_upload_component import FileUploadComponent
from infrastructure.ui.components.delete_analysis_component import DeleteAnalysisComponent


class SidebarComponent:
    """
    Componente que maneja la renderización completa del sidebar.
    """
    
    def __init__(self, controller: StreamlitController):
        """
        Inicializa el componente del sidebar.
        
        Args:
            controller: Controlador de Streamlit para interactuar con casos de uso
        """
        self._controller = controller
        self._file_upload = FileUploadComponent()
        self._delete_analysis = DeleteAnalysisComponent(controller)
    
    def render(self) -> Tuple[Optional[object], Optional[str]]:
        """
        Renderiza la interfaz de usuario de la barra lateral.
        
        Returns:
            Una tupla que contiene el objeto de archivo cargado y el nombre del
            análisis a cargar, o None para cualquiera si no aplica.
        """
        st.sidebar.title("Controles")
        analysis_to_load = None
        
        # Inicializar session_state para el análisis seleccionado
        if 'selected_analysis' not in st.session_state:
            st.session_state.selected_analysis = None
        
        # Renderizar componente de carga de archivos
        uploaded_file = self._file_upload.render()
        
        # Renderizar sección de análisis guardados
        analysis_to_load = self._render_saved_analyses()
        
        # Renderizar componente de eliminación
        saved_analyses = self._controller.get_saved_analyses()
        self._delete_analysis.render(saved_analyses)
        
        return uploaded_file, analysis_to_load
    
    def _render_saved_analyses(self) -> Optional[str]:
        """
        Renderiza la sección de análisis guardados.
        
        Returns:
            Nombre del análisis a cargar o None
        """
        st.sidebar.header("📂 Ver Análisis Guardado")
        saved_analyses = self._controller.get_saved_analyses()
        
        if not saved_analyses:
            st.sidebar.info("No hay análisis guardados en la base de datos.")
            st.session_state.selected_analysis = None
            return None
        
        # Usar índice para mantener la selección actual
        current_index = 0
        if 'selected_analysis' in st.session_state and st.session_state.selected_analysis in saved_analyses:
            current_index = saved_analyses.index(st.session_state.selected_analysis)
        
        selected_analysis = st.sidebar.selectbox(
            "Seleccionar análisis", 
            saved_analyses,
            index=current_index,
            key="analysis_selectbox"
        )
        
        # Detectar cambios en el selectbox y actualizar automáticamente
        if selected_analysis != st.session_state.get('selected_analysis'):
            st.session_state.selected_analysis = selected_analysis
            return selected_analysis
        
        return None

