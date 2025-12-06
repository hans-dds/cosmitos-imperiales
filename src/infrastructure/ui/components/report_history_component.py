"""Componente de UI para historial de reportes generados."""

import os
import streamlit as st


class ReportHistoryComponent:
    def render(self, controller):
        st.subheader("Historial de Reportes")
        self._render_actions(controller)
        reports = controller.get_report_history()
        if not reports:
            st.info("No hay reportes guardados aún.")
            return
        for r in reports:
            # Ajuste de layout: tipo y fecha más cercanos y compactos
            cols = st.columns([3, 1, 2, 1, 1])
            with cols[0]:
                base = r.get("source_file_name") or r.get("analysis_name")
                st.write(f"📄 {base}")
            with cols[1]:
                st.write(r["report_format"].upper())
            with cols[2]:
                dr = r.get("date_range") or "-"
                st.write(f"{str(r['created_at'])} | {dr}")
            with cols[3]:
                path = r["file_path"]
                ok, data = controller.get_report_bytes(path)
                if not ok or data is None:
                    st.button(
                        "Archivo no disponible",
                        disabled=True,
                        key=f"missing_{r['id']}",
                    )
                else:
                    st.download_button(
                        label="⬇️",
                        data=data,
                        file_name=os.path.basename(path),
                        mime="application/pdf"
                        if path.endswith(".pdf")
                        else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"dl_{r['id']}",
                    )
            with cols[4]:
                if st.button("🗑️", key=f"del_{r['id']}"):
                    ok, msg = controller.delete_report(r["id"])
                    if ok:
                        st.toast(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    def _render_actions(self, controller) -> None:
        with st.expander("Acciones", expanded=False):
            if st.button("🧹 Limpiar historial", type="primary"):
                ok, msg = controller.clear_report_history()
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
