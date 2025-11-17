"""
Punto de entrada principal de la aplicación Streamlit.

Este módulo se encarga únicamente de:
- Configurar la página
- Inicializar el contenedor de dependencias
- Orquestar la renderización de componentes principales
"""

import streamlit as st

from infrastructure.dependency_injection_container import container
from infrastructure.ui.config import config_page
from infrastructure.ui.sidebar import show_sidebar
from infrastructure.ui.components.main_content import MainContent


def main():
    """
    Función principal que ejecuta la aplicación Streamlit.
    
    Esta función actúa como punto de entrada y se limita a:
    1. Configurar la página
    2. Obtener dependencias del contenedor
    3. Renderizar componentes principales
    """
    # Configurar página
    config_page()
    st.title("Gestor de Satisfacción y Seguimiento de Posventa")

    # Obtener dependencias del contenedor
    controller = container.streamlit_controller
    list_analyses_use_case = container.list_analyses_use_case
    delete_analysis_use_case = container.delete_analysis_use_case

    # Renderizar barra lateral y obtener entrada del usuario
    uploaded_file, analysis_to_load = show_sidebar(
        list_analyses_use_case,
        delete_analysis_use_case
    )

    # Renderizar contenido principal
    main_content = MainContent(controller)
    main_content.render(uploaded_file, analysis_to_load)


if __name__ == "__main__":
    main()
