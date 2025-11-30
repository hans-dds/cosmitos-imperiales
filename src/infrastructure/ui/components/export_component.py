"""Componente para exportar análisis a Excel y PDF."""

import streamlit as st
import pandas as pd
from typing import Dict

from infrastructure.ui.export import generate_excel_export
from infrastructure.ui.export_pdf import generate_pdf_export
from infrastructure.dependency_injection_container import container


class ExportComponent:
    """Componente responsable de la exportación de análisis."""

    def render(self, df: pd.DataFrame, analysis_name: str, color_map: Dict[str, str]):
        """
        Renderiza los controles de exportación disponibles.

        Args:
            df: DataFrame con los datos a exportar
            analysis_name: Nombre del análisis
            color_map: Mapa de colores usado por las visualizaciones principales
        """
        st.subheader("Exportar y Compartir")
        
        excel_file_name = f"reporte_{analysis_name.replace(' ', '_')}.xlsx"
        pdf_file_name = excel_file_name.replace('.xlsx', '.pdf')

        col_excel, col_pdf = st.columns(2)

        with col_excel:
            st.download_button(
                label="📎 Descargar Reporte en Excel",
                data=generate_excel_export(df),
                file_name=excel_file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        with col_pdf:
            try:
                pdf_bytes = generate_pdf_export(df, color_map)
            except ValueError as error:
                st.info(f"PDF no disponible: {error}")
            else:
                st.download_button(
                    label="🖨️ Descargar Reporte en PDF",
                    data=pdf_bytes,
                    file_name=pdf_file_name,
                    mime="application/pdf"
                )

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
                    # Procesar correos
                    to_emails = [email.strip() for email in emails_input.split(",") if email.strip()]
                    
                    if not to_emails:
                        st.warning("No se detectaron correos válidos.")
                    else:
                        with st.spinner(f"Enviando correo a {len(to_emails)} destinatarios..."):
                            controller = container.streamlit_controller
                            success, message = controller.handle_send_email(
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
