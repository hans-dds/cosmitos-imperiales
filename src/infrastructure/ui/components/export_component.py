"""Componente para exportar análisis a Excel."""

import streamlit as st
import pandas as pd

from infrastructure.ui.export import generate_excel_export


class ExportComponent:
    """Componente responsable de la exportación de análisis."""

    def render(self, df: pd.DataFrame, analysis_name: str):
        """
        Renderiza el botón de descarga de Excel.

        Args:
            df: DataFrame con los datos a exportar
            analysis_name: Nombre del análisis
        """
        file_name = f"reporte_{analysis_name.replace(' ', '_')}.xlsx"

        st.download_button(
            label="📎 Descargar Reporte en Excel",
            data=generate_excel_export(df),
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument."
                 "spreadsheetml.sheet"
        )
