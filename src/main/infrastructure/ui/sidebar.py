import streamlit as st
from typing import Tuple, Optional
from use_cases.list_analyses_use_case import ListAnalysesUseCase
from use_cases.delete_analysis_use_case import DeleteAnalysisUseCase


def show_sidebar(
    list_analyses_use_case: ListAnalysesUseCase,
    delete_analysis_use_case: DeleteAnalysisUseCase
) -> Tuple[Optional[object], Optional[str]]:
    """
    Renderiza la interfaz de usuario de la barra lateral, incluyendo el
    cargador de archivos y la lista de análisis guardados.

    Args:
        list_analyses_use_case: El caso de uso para listar análisis guardados.
        delete_analysis_use_case: El caso de uso para eliminar análisis guardados.

    Returns:
        Una tupla que contiene el objeto de archivo cargado y el nombre del
        análisis a cargar, o None para cualquiera si no aplica.
    """
    st.sidebar.title("Controles")
    analysis_to_load = None

    # Inicializar session_state para el análisis seleccionado
    if 'selected_analysis' not in st.session_state:
        st.session_state.selected_analysis = None

    # --- Cargador de Archivos ---
    st.sidebar.header("📁 Cargar y Analizar Archivo")
    uploaded_file = st.sidebar.file_uploader(
        "Sube un archivo CSV o Excel", type=["csv", "xlsx"])
    
    # Si se sube un nuevo archivo (diferente al último procesado), limpiar la selección
    if uploaded_file:
        file_id = f"{uploaded_file.name}_{uploaded_file.size}"
        # Solo limpiar si es un archivo nuevo, no si ya fue procesado
        if 'last_processed_file' not in st.session_state or st.session_state.last_processed_file != file_id:
            st.session_state.selected_analysis = None

    # --- Análisis Guardados ---
    st.sidebar.header("📂 Ver Análisis Guardado")
    saved_analyses = list_analyses_use_case.execute()
    if not saved_analyses:
        st.sidebar.info("No hay análisis guardados en la base de datos.")
        st.session_state.selected_analysis = None
    else:
        # Usar índice para mantener la selección actual
        current_index = 0
        if 'selected_analysis' in st.session_state and st.session_state.selected_analysis in saved_analyses:
            current_index = saved_analyses.index(st.session_state.selected_analysis)
        
        selected_analysis = st.sidebar.selectbox(
            "Seleccionar análisis", 
            saved_analyses,
            index=current_index,
            key="analysis_selectbox")
        
        # Detectar cambios en el selectbox y actualizar automáticamente
        if selected_analysis != st.session_state.get('selected_analysis'):
            st.session_state.selected_analysis = selected_analysis
            analysis_to_load = selected_analysis

        # Sección para eliminar análisis
        st.sidebar.markdown("---")
        st.sidebar.subheader("🗑️ Eliminar Análisis")
        
        # Inicializar estado para análisis seleccionados para eliminar
        if 'analyses_to_delete' not in st.session_state:
            st.session_state.analyses_to_delete = []
        
        
        # Multiselect para seleccionar análisis a eliminar
        selected_to_delete = st.sidebar.multiselect(
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
            num_selected = len(st.session_state.analyses_to_delete)
            delete_label = f"🗑️ Eliminar {num_selected} análisis seleccionado{'s' if num_selected > 1 else ''}"
            
            # Usar un estado para confirmar la eliminación
            if 'confirm_delete' not in st.session_state:
                st.session_state.confirm_delete = False
            
            if not st.session_state.confirm_delete:
                if st.sidebar.button(delete_label, type="secondary", use_container_width=True, key="delete_button"):
                    st.session_state.confirm_delete = True
                    st.rerun()
            else:
                if num_selected == len(saved_analyses):
                    st.sidebar.warning("⚠️ ¿Eliminar TODOS los análisis? Esta acción no se puede deshacer.")
                else:
                    st.sidebar.warning(f"⚠️ ¿Eliminar {num_selected} análisis seleccionado{'s' if num_selected > 1 else ''}?")
                    st.sidebar.write("Análisis a eliminar:")
                    for analysis in st.session_state.analyses_to_delete:
                        st.sidebar.write(f"  • {analysis}")
                
                col1, col2 = st.sidebar.columns(2)
                with col1:
                    confirm_btn = st.sidebar.button(
                        "Confirmar", 
                        use_container_width=True, 
                        key="confirm_delete_btn",
                        type="primary"
                    )
                    
                    if confirm_btn:
                        # Eliminar los análisis seleccionados
                        all_success, results = delete_analysis_use_case.execute_multiple(
                            st.session_state.analyses_to_delete
                        )
                        
                        # Mostrar resultados
                        success_count = sum(1 for _, success, _ in results if success)
                        error_count = len(results) - success_count
                        
                        if all_success:
                            st.sidebar.success(f"✅ {success_count} análisis eliminado{'s' if success_count > 1 else ''} exitosamente.")
                        else:
                            st.sidebar.warning(f"⚠️ {success_count} eliminado{'s' if success_count > 1 else ''}, {error_count} error{'es' if error_count > 1 else ''}.")
                            # Mostrar errores individuales
                            for name, success, message in results:
                                if not success:
                                    st.sidebar.error(f"❌ {name}: {message}")
                        
                        # Limpiar estados relacionados
                        deleted_names = st.session_state.analyses_to_delete.copy()
                        if st.session_state.get('selected_analysis') in deleted_names:
                            st.session_state.selected_analysis = None
                        if st.session_state.get('last_loaded_analysis') in deleted_names:
                            st.session_state.last_loaded_analysis = None
                        if 'df_display' in st.session_state and st.session_state.get('analysis_name') in deleted_names:
                            del st.session_state.df_display
                        
                        # Limpiar selección
                        st.session_state.analyses_to_delete = []
                        st.session_state.confirm_delete = False
                        st.rerun()
                
                with col2:
                    cancel_btn = st.sidebar.button(
                        "Cancelar", 
                        use_container_width=True, 
                        key="cancel_delete_btn"
                    )
                    
                    if cancel_btn:
                        st.session_state.confirm_delete = False
                        st.rerun()
        else:
            st.sidebar.info("Selecciona uno o más análisis para eliminar.")

    return uploaded_file, analysis_to_load
