"""
Componente para manejar la eliminación de análisis en el sidebar.
"""

import streamlit as st
from typing import List
from infrastructure.ui.controllers.streamlit_controller import \
    StreamlitController


class DeleteAnalysisComponent:
    """
    Componente que maneja la UI y lógica de eliminación de análisis.
    """

    def __init__(self, controller: StreamlitController):
        """
        Inicializa el componente.
        Args:
            controller: Controlador de Streamlit para interactuar con
            casos de uso
        """
        self._controller = controller

    def render(self, saved_analyses: List[str], embedded: bool = False):
        """
        Renderiza el componente de eliminación de análisis.
        Args:
            saved_analyses: Lista de nombres de análisis guardados
        """
        if not saved_analyses:
            return
        if not embedded:
            expander_ctx = st.sidebar.expander("🗑️ Eliminar análisis", expanded=False)
        else:
            expander_ctx = st.expander("🗑️ Eliminar análisis", expanded=False)

        with expander_ctx:
            # Inicializar estado para análisis seleccionados para eliminar
            if 'analyses_to_delete' not in st.session_state:
                st.session_state.analyses_to_delete = []
            # Multiselect para seleccionar análisis a eliminar
            selected_to_delete = st.multiselect(
                "Análisis seleccionados:",
                saved_analyses,
                default=st.session_state.analyses_to_delete,
                key="delete_multiselect",
                placeholder="Selecciona los análisis a eliminar"
            )
            # Actualizar el estado con la selección del multiselect
            st.session_state.analyses_to_delete = selected_to_delete
            # Botón para eliminar los análisis seleccionados
            if st.session_state.analyses_to_delete:
                self._render_delete_confirmation(saved_analyses)
            else:
                st.info("Selecciona uno o más análisis para eliminar.")

    def _render_delete_confirmation(self, saved_analyses: List[str]):
        """
        Renderiza la confirmación de eliminación.
        Args:
            saved_analyses: Lista de nombres de análisis guardados
        """
        num_selected = len(st.session_state.analyses_to_delete)
        delete_label = (f"Eliminar {num_selected} análisis "
                        f"seleccionado{'s' if num_selected > 1 else ''}")
        # Usar un estado para confirmar la eliminación
        if 'confirm_delete' not in st.session_state:
            st.session_state.confirm_delete = False
        if not st.session_state.confirm_delete:
            if st.button(
                    delete_label,
                    type="secondary",
                    use_container_width=True,
                    key="delete_button"):
                st.session_state.confirm_delete = True
                st.rerun()
        else:
            self._show_confirmation_ui(num_selected, saved_analyses)

    def _show_confirmation_ui(
            self,
            num_selected: int,
            saved_analyses: List[str]):
        """
        Muestra la UI de confirmación de eliminación.
        Args:
            num_selected: Número de análisis seleccionados
            saved_analyses: Lista de nombres de análisis guardados
        """
        if num_selected == len(saved_analyses):
            st.warning(
                "⚠️ ¿Eliminar TODOS los análisis? Esta acción no se puede"
                " deshacer.")
        else:
            st.warning(
                f"⚠️ ¿Eliminar {num_selected} análisis seleccionado"
                f"{'s' if num_selected > 1 else ''}?")
            st.write("Análisis a eliminar:")
            for analysis in st.session_state.analyses_to_delete:
                st.write(f"  • {analysis}")
        col1, col2 = st.columns(2)
        with col1:
            confirm_btn = st.button(
                "Confirmar",
                use_container_width=True,
                key="confirm_delete_btn",
                type="primary"
            )
        with col2:
            cancel_btn = st.button(
                "Cancelar",
                use_container_width=True,
                key="cancel_delete_btn"
            )
        # Ejecutar acciones fuera del contexto de las columnas para que los mensajes ocupen todo el ancho
        if confirm_btn:
            self._execute_deletion()
        if cancel_btn:
            st.session_state.confirm_delete = False
            st.rerun()

    def _execute_deletion(self):
        """
        Ejecuta la eliminación de los análisis seleccionados.
        """
        # Eliminar los análisis seleccionados
        all_success, results = \
            self._controller.handle_delete_multiple_analyses(
                st.session_state.analyses_to_delete
            )
        # Mostrar resultados
        success_count = sum(1 for _, success, _ in results if success)
        error_count = len(results) - success_count
        if all_success:
            st.success(
                f"{success_count} análisis eliminado"
                f"{'s' if success_count > 1 else ''} exitosamente.")
        else:
            st.warning(
                f"⚠️ {success_count} eliminado"
                f"{'s' if success_count > 1 else ''}, "
                f"{error_count} error{'es' if error_count > 1 else ''}."
            )
            # Mostrar errores individuales
            for name, success, message in results:
                if not success:
                    st.error(f"❌ {name}: {message}")
        # Limpiar estados relacionados
        deleted_names = st.session_state.analyses_to_delete.copy()
        if st.session_state.get('selected_analysis') in deleted_names:
            st.session_state.selected_analysis = None
        if st.session_state.get('last_loaded_analysis') in deleted_names:
            st.session_state.last_loaded_analysis = None
        if 'df_display' in st.session_state and st.session_state.get(
                'analysis_name') in deleted_names:
            del st.session_state.df_display
        # Limpiar selección
        st.session_state.analyses_to_delete = []
        st.session_state.confirm_delete = False
        st.rerun()
