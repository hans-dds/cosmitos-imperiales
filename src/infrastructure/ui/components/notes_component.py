import streamlit as st
from use_cases.manage_notes_use_case import ManageNotesUseCase

class NotesComponent:
    def __init__(self, use_case: ManageNotesUseCase):
        self._use_case = use_case

    def render(self, analysis_name: str):
        st.markdown("---")
        st.subheader("Notas y Hallazgos del Ejecutivo")
        
        # 1. Sección para agregar nueva nota
        with st.form(key="add_note_form", clear_on_submit=True):
            new_note = st.text_area("Agregar nuevo hallazgo:", height=100)
            submit = st.form_submit_button("Guardar Nota")
            
            if submit and new_note:
                if self._use_case.add_note(analysis_name, new_note):
                    st.success("Nota guardada.")
                    st.rerun()
                else:
                    st.error("Error al guardar la nota.")

        # 2. Listar notas existentes
        notes = self._use_case.get_notes(analysis_name)
        
        if notes:
            st.write(f"**Hallazgos registrados ({len(notes)}):**")
            for note in notes:
                with st.expander(f"Nota del {note['fecha_creacion']}", expanded=True):
                    # Mostrar contenido
                    st.markdown(note['contenido'])
                    
                    # Botón de eliminar
                    col_del, col_space = st.columns([1, 5])
                    with col_del:
                        if st.button("🗑️ Eliminar", key=f"del_{note['id']}"):
                            self._use_case.delete_note(note['id'])
                            st.rerun()
        else:
            st.info("No hay hallazgos registrados para este análisis.")