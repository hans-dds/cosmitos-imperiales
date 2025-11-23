"""Componente para exportar análisis a Excel y PDF."""

import streamlit as st
import pandas as pd
from typing import Dict

from infrastructure.ui.export import generate_excel_export
from infrastructure.ui.export_pdf import generate_pdf_export


class ExportComponent:
    """Componente responsable de la exportación de análisis."""

    def render(self,
               df: pd.DataFrame,
               analysis_name: str,
               color_map: Dict[str, str]):
        """
        Renderiza los controles de exportación disponibles.

        Args:
            df: DataFrame con los datos a exportar
            analysis_name: Nombre del análisis
            color_map: Mapa de colores usado
                por las visualizaciones principales
        """
        excel_file_name = f"reporte_{analysis_name.replace(' ', '_')}.xlsx"
        pdf_file_name = excel_file_name.replace('.xlsx', '.pdf')

        col_excel, col_pdf = st.columns(2)

        with col_excel:
            st.download_button(
                label="📎 Descargar Reporte en Excel",
                data=generate_excel_export(df),
                file_name=excel_file_name,
                mime="application/vnd.openxmlformats" +
                     "-officedocument.spreadsheetml.sheet"
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
