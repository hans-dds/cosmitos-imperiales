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
    delete_analysis_use_case = container.delete_analysis_use_case

    # Renderizar barra lateral y obtener entrada del usuario
    uploaded_file, analysis_to_load = show_sidebar(
        list_analyses_use_case, 
        delete_analysis_use_case
    )

    # --- Área de Contenido Principal ---

    # Lógica para procesar un nuevo archivo (debe ir primero para establecer el estado correcto)
    # Usar un flag para evitar procesar el mismo archivo múltiples veces
    if uploaded_file:
        # Verificar si este archivo ya fue procesado en esta sesión
        file_id = f"{uploaded_file.name}_{uploaded_file.size}"
        if 'last_processed_file' not in st.session_state or st.session_state.last_processed_file != file_id:
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

                # Obtener el nombre de la tabla creada (formato: analisis_{file_basename})
                new_analysis_name = f"analisis_{file_basename}"
                
                st.success(
                    f"Archivo '{uploaded_file.name}'"
                    " procesado y guardado exitosamente.")
                
                # Establecer el análisis recién creado como el seleccionado
                st.session_state.selected_analysis = new_analysis_name
                st.session_state.last_loaded_analysis = new_analysis_name
                st.session_state.df_display = analyzed_df
                st.session_state.analysis_name = new_analysis_name
                st.session_state.last_processed_file = file_id
                
                # Limpiar selecciones de eliminación
                if 'analyses_to_delete' in st.session_state:
                    st.session_state.analyses_to_delete = []
                if 'confirm_delete' in st.session_state:
                    st.session_state.confirm_delete = False
                # Forzar actualización del sidebar para mostrar el nuevo análisis
                st.rerun()

            except Exception as e:
                st.error(f"Ocurrió un error al procesar el archivo: {e}")
                # Limpiar el flag en caso de error para permitir reintentar
                if 'last_processed_file' in st.session_state:
                    del st.session_state.last_processed_file

    # Lógica para cargar un análisis guardado (después de procesar archivos)
    # Solo cargar si no tenemos datos ya cargados para el análisis seleccionado
    selected_analysis = st.session_state.get('selected_analysis')
    current_analysis_name = st.session_state.get('analysis_name')
    
    # Verificar si necesitamos cargar un análisis
    needs_load = False
    if analysis_to_load:
        needs_load = True
    elif selected_analysis and selected_analysis != st.session_state.get('last_loaded_analysis'):
        # Solo cargar si el análisis actual no coincide con el seleccionado
        if current_analysis_name != selected_analysis:
            needs_load = True
    
    if needs_load:
        analysis_name = analysis_to_load or selected_analysis
        try:
            loaded_df = load_analysis_use_case.execute(analysis_name)
            if not loaded_df.empty:
                st.session_state.df_display = loaded_df
                st.session_state.analysis_name = analysis_name
                st.session_state.last_loaded_analysis = analysis_name
            else:
                st.warning(f"No se encontraron datos para el análisis '{analysis_name}'.")
                # Limpiar el estado si no hay datos
                if 'df_display' in st.session_state:
                    del st.session_state.df_display
        except Exception as e:
            st.error(f"Error al cargar el análisis '{analysis_name}': {e}")

    # Mostrar el DataFrame actual (recién procesado o cargado)
    if 'df_display' in st.session_state:
        st.header(st.session_state.analysis_name)
        df_to_show = st.session_state.df_display

        if not df_to_show.empty:
            if 'comentarios' in df_to_show.columns and 'longitud' \
                    not in df_to_show.columns:
                df_to_show['longitud'] = df_to_show['comentarios'].str.len()

            color_map = {
                'Promotor': '#00CC96',   # Verde para promotores
                'Detractor': '#EF553B',  # Rojo para detractores
                'Neutro': '#636EFA'      # Azul para neutros
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
