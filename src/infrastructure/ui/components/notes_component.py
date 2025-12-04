import streamlit as st
from infrastructure.ui.controllers.streamlit_controller import StreamlitController

class NotesComponent:
    def render(self, controller: StreamlitController, analysis_name: str):
        st.markdown("---")
        st.subheader("Notas y Hallazgos")
        
        # 1. Listar notas existentes
        notes = controller.get_notes(analysis_name)
        if notes:
            for note in notes:
                with st.expander(f"Nota del {note['created_at']}"):
                    st.write(note['note_content'])
                    if st.button("🗑️ Eliminar", key=f"del_note_{note['id']}"):
                        success, msg = controller.delete_note(note['id'])
                        if success:
                            st.rerun()
                        else:
                            st.error(msg)
        else:
            st.info("No hay notas guardadas para este reporte.")

        # 2. Formulario para nueva nota
        with st.form(key="new_note_form"):
            content = st.text_area("Nueva nota:", placeholder="Escribe un hallazgo...")
            if st.form_submit_button("Guardar Nota"):
                success, msg = controller.add_note(analysis_name, content)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)