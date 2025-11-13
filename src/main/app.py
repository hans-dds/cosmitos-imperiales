import pandas as pd
import streamlit as st

from infrastructure.dependency_injection_container import container
from infrastructure.ui.charts import show_charts
from infrastructure.ui.config import config_page
from infrastructure.ui.export import generate_excel_export
from infrastructure.ui.sidebar import show_sidebar
from infrastructure.ui.tables import show_comments_table


def main():
    """La función principal que ejecuta la aplicación Streamlit."""
    config_page()
    st.title("Gestor de Satisfacción y Seguimiento de Posventa")

    # Obtener servicios del contenedor
    process_use_case = container.process_file_use_case
    list_analyses_use_case = container.list_analyses_use_case
    load_analysis_use_case = container.load_analysis_use_case

    # Renderizar barra lateral y obtener entrada del usuario
    uploaded_file, analysis_to_load = show_sidebar(list_analyses_use_case)

    # --- Área de Contenido Principal ---

    # Lógica para cargar un análisis guardado
    if analysis_to_load:
        st.session_state.df_display = load_analysis_use_case.execute(
            analysis_to_load)
        st.session_state.analysis_name = analysis_to_load

    # Lógica para procesar un nuevo archivo
    if uploaded_file:
        file_basename = uploaded_file.name.split('.')[0]
        try:
            # Leer archivo en DataFrame
            if uploaded_file.type == "text/csv":
                raw_df = pd.read_csv(uploaded_file)
            else:
                # Esta lógica estaba en el antiguo `ServicioLimpiarDatos`
                raw_df_dict = pd.read_excel(uploaded_file, sheet_name=None)
                required_sheets = ["ATC", "Encuesta salida"]
                df_list = [
                    df_sheet for sheet_name, df_sheet in raw_df_dict.items()
                    if sheet_name in required_sheets
                ]
                raw_df = pd.concat(df_list, ignore_index=True)

            with st.spinner(
                    "Procesando archivo... Esto puede tardar unos segundos."):
                analyzed_df = process_use_case.execute(raw_df, file_basename)

            st.success(
                f"Archivo '{uploaded_file.name}'"
                " procesado y guardado exitosamente.")
            st.session_state.df_display = analyzed_df
            st.session_state.analysis_name = f"Nuevo Análisis: {file_basename}"

        except Exception as e:
            st.error(f"Ocurrió un error al procesar el archivo: {e}")

    # Mostrar el DataFrame actual (recién procesado o cargado)
    if 'df_display' in st.session_state:
        st.header(st.session_state.analysis_name)
        df_to_show = st.session_state.df_display

        if not df_to_show.empty:
            if 'comentarios' in df_to_show.columns and 'longitud' \
                    not in df_to_show.columns:
                df_to_show['longitud'] = df_to_show['comentarios'].str.len()

            color_map = {
                'Positivo': '#00CC96',
                'Negativo': '#EF553B',
                'Neutro': '#636EFA'
                }
            show_charts(df_to_show, color_map)
            show_comments_table(df_to_show)

            st.download_button(
                label="📎 Descargar Reporte en Excel",
                data=generate_excel_export(df_to_show),
                file_name="reporte_"
                + f"{st.session_state.analysis_name.replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            )
        else:
            st.warning(
                "No hay datos para mostrar en el análisis seleccionado.")


if __name__ == "__main__":
    main()
