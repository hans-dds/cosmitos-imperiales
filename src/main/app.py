from presentacion.vista.charts import mostrar_graficos
import streamlit as st
from presentacion.controlador.loader import get_services, process_uploaded_file
from presentacion.vista.layout import show_header, show_tables, show_comments_table, show_export_button
import presentacion.vista.config_app_ui as cau
from presentacion.vista.layout import upload_file_view
from presentacion.vista.utils import color_discrete_map
from presentacion.vista.word_cloud import show_word_cloud
import pandas as pd


cau.config_page()
show_header()

# Get services
sld, sae = get_services()

# --- Sidebar ---
st.sidebar.title("Análisis Guardados")
lista_analisis = sae.listar_analisis_guardados()

if not lista_analisis:
    st.sidebar.info("No hay análisis guardados.")
else:
    analisis_seleccionado = st.sidebar.selectbox(
        "Seleccionar un análisis para ver", lista_analisis
    )
    if st.sidebar.button("Cargar Análisis"):
        df_cargado = sae.cargar_analisis_por_nombre(analisis_seleccionado)
        if df_cargado is not None and not df_cargado.empty:
            st.session_state['df_actual'] = df_cargado
            st.session_state['analisis_actual'] = analisis_seleccionado
        else:
            st.sidebar.error("No se pudieron cargar los datos del análisis.")

# Display loaded analysis from sidebar
if 'df_actual' in st.session_state:
    st.subheader(f"Mostrando análisis: {st.session_state['analisis_actual']}")
    df_display = st.session_state['df_actual']
    if 'comentarios' in df_display.columns:
        df_display['longitud'] = df_display['comentarios'].str.len()
    else:
        df_display['longitud'] = 0
    show_comments_table(df_display)
    show_word_cloud(df_display)
    mostrar_graficos(df_display, color_discrete_map)
    show_export_button(df_display)


#st.markdown("---")

# File uploader
archivo = upload_file_view()
if archivo:
    datos, mensaje, valido = process_uploaded_file(archivo, sld, sae)

    if valido:
        st.sidebar.success(mensaje)
        #st.subheader("Resultados del Nuevo Análisis")
        df = datos
        if df is not None and not df.empty:
            #st.dataframe(df.head(5), use_container_width=True, hide_index=True)
            show_comments_table(df)
            show_word_cloud(df)
            mostrar_graficos(df, color_discrete_map)
            show_export_button(df)

            if st.button("Guardar Resultados"):
                file_name_base = archivo.name.split('.')[0]
                table_name = f"analisis_{file_name_base}"
                guardado_exitoso, mensaje_guardado = sae.guardar_analisis(
                    df, file_name_base, table_name
                )
                if guardado_exitoso:
                    st.success("Resultados guardados exitosamente.")
                    st.info(mensaje_guardado)
                    # Refresh saved analyses list
                    st.rerun()
                else:
                    st.error("Error al guardar los resultados.")
                    st.warning(mensaje_guardado)



        elif df is not None and df.empty:
            st.warning("El archivo se procesó, pero no se encontraron "
                       "comentarios válidos después de la limpieza.")
        else:
            st.warning("No se pudieron cargar los datos correctamente.")
    else:
        st.sidebar.error(mensaje)