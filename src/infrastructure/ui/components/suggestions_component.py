import streamlit as st
from typing import List
from domain.entities.suggestion import Suggestion

class SuggestionsComponent:
    """
    Componente responsable de renderizar la sección
    "Sugerencias de Mejora" (HU-17).
    """

    def render(self, suggestions: List[Suggestion]):
        """
        Renderiza la sección de sugerencias.

        Args:
            suggestions: La lista de entidades Suggestion (ya filtrada a 3).
        """
        
        st.subheader("💡 Sugerencias de Mejora")

        # Criterio de Aceptación: Mensaje positivo si no hay sugerencias
        if not suggestions:
            st.info(
                "¡Buen trabajo! No se han identificado áreas críticas de "
                "mejora en los comentarios de los detractores para este período."
            )
            return

        # Criterio de Aceptación: Mostrar las sugerencias
        # Usamos st.metric para un buen formato
        
        cols = st.columns(len(suggestions))
        
        for i, suggestion in enumerate(suggestions):
            with cols[i]:
                st.metric(
                    label=suggestion.theme,      # Tema (Ej: "Tiempos de Espera")
                    value=suggestion.recommendation # Sugerencia
                )
        
        # Criterio de Aceptación (del Mockup): Botón "Ver todas"
        st.button("Ver todas las sugerencias", disabled=True, 
                  help="Funcionalidad futura para ver historial de sugerencias.")
