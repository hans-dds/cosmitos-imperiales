"""Componente para exportar análisis a Excel y PDF."""

import streamlit as st
import pandas as pd
from typing import Dict

from infrastructure.ui.export import generate_excel_export
from infrastructure.ui.export_pdf import generate_pdf_export
from infrastructure.ui.components.report_history_component import ReportHistoryComponent


class ExportComponent:
    """Componente responsable de la exportación de análisis."""

    def __init__(self, controller):
        self._controller = controller

    def render(self, df: pd.DataFrame, analysis_name: str, color_map: Dict[str, str]):
        """
        Renderiza los controles de exportación disponibles.

        Args:
            df: DataFrame con los datos a exportar
            analysis_name: Nombre del análisis
            color_map: Mapa de colores usado por las visualizaciones principales
        """
        st.subheader("Exportar y Compartir")

        tab_export, tab_historial = st.tabs(["Exportar", "Historial de Reportes"])

        with tab_export:
            excel_file_name = f"reporte_{analysis_name.replace(' ', '_')}.xlsx"
            pdf_file_name = excel_file_name.replace('.xlsx', '.pdf')

            col_excel, col_pdf = st.columns(2)

            with col_excel:
                excel_bytes = generate_excel_export(df)
                clicked = st.download_button(
                    label="📎 Descargar Reporte en Excel",
                    data=excel_bytes,
                    file_name=excel_file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                if clicked:
                    success, message, path = self._controller.handle_save_report(
                        analysis_name=analysis_name,
                        df=df,
                        report_format='excel'
                    )
                    if success:
                        st.toast("Reporte Excel guardado en historial")
                    else:
                        st.warning(f"No se pudo guardar en historial: {message}")

            with col_pdf:
                try:
                    pdf_bytes = generate_pdf_export(df, color_map)
                except ValueError as error:
                    st.info(f"PDF no disponible: {error}")
                else:
                    clicked_pdf = st.download_button(
                        label="🖨️ Descargar Reporte en PDF",
                        data=pdf_bytes,
                        file_name=pdf_file_name,
                        mime="application/pdf"
                    )
                    if clicked_pdf:
                        success, message, path = self._controller.handle_save_report(
                            analysis_name=analysis_name,
                            df=df,
                            report_format='pdf',
                            color_map=color_map,
                        )
                        if success:
                            st.toast("Reporte PDF guardado en historial")
                        else:
                            st.warning(f"No se pudo guardar en historial: {message}")

            st.markdown("---")
            st.write("📧 **Enviar reporte por correo**")

            with st.form("email_form"):
                emails_input = st.text_area(
                    "Correos electrónicos (separados por coma)",
                    placeholder="ejemplo@empresa.com, jefe@empresa.com",
                    help="Ingresa los correos a los que deseas enviar el reporte."
                )

                attachment_format = st.radio(
                    "Formato del adjunto",
                    options=["Excel", "PDF"],
                    horizontal=True
                )

                submitted = st.form_submit_button("Enviar Reporte")

                if submitted:
                    if not emails_input:
                        st.warning("Por favor ingresa al menos un correo electrónico.")
                    else:
                        to_emails = [email.strip() for email in emails_input.split(",") if email.strip()]

                        if not to_emails:
                            st.warning("No se detectaron correos válidos.")
                        else:
                            with st.spinner(f"Enviando correo a {len(to_emails)} destinatarios..."):
                                success, message = self._controller.handle_send_email(
                                    to_emails=to_emails,
                                    analysis_name=analysis_name,
                                    df=df,
                                    attachment_type=attachment_format.lower(),
                                    color_map=color_map
                                )

                                if success:
                                    st.success(message)
                                else:
                                    st.error(message)

        with tab_historial:
            ReportHistoryComponent().render(self._controller)

            # Botón rápido en la parte superior para ir al historial desde otros lugares
            st.caption("Tip: usa las pestañas arriba para cambiar de vista.")
