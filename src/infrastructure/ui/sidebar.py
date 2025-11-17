"""
Módulo que proporciona la función show_sidebar para mantener compatibilidad.
"""

from typing import Tuple, Optional
from infrastructure.ui.components.sidebar_component import SidebarComponent
from infrastructure.ui.controllers.streamlit_controller import StreamlitController


def show_sidebar(controller: StreamlitController) -> Tuple[Optional[object], Optional[str]]:
    """
    Renderiza la interfaz de usuario de la barra lateral.
    
    Esta función actúa como un wrapper para mantener compatibilidad
    con el código existente, delegando al SidebarComponent.

    Args:
        controller: Controlador de Streamlit para interactuar con casos de uso

    Returns:
        Una tupla que contiene el objeto de archivo cargado y el nombre del
        análisis a cargar, o None para cualquiera si no aplica.
    """
    sidebar_component = SidebarComponent(controller)
    return sidebar_component.render()
