from presentacion.vista.charts import mostrar_graficos
import streamlit as st
from presentacion.controlador.loader import get_services, process_uploaded_file
from presentacion.vista.layout import show_header, show_tables, show_comments_table, show_export_button
import presentacion.vista.config_app_ui as cau
from presentacion.vista.layout import upload_file_view
from presentacion.vista.utils import color_discrete_map
import pandas as pd

# ===============================
# CONFIGURACIÓN INICIAL
# ===============================
cau.config_page()
show_header()

# ===============================
# CSS GLOBAL: AJUSTE AUTOMÁTICO Y SIN CORTES
# ===============================
st.markdown("""
<style>
/* Ajuste general de página */
html, body {
    width: 100%;
    max-width: 100%;
    overflow-x: hidden;
    margin: 0;
    padding: 0;
    zoom: 1.0;
    background-color: white;
}

/* Contenedor principal adaptable */
main, .block-container {
    max-width: 95vw;
    margin: auto;
    padding: 0 1rem;
}

/* Gráficas de Plotly */
.plotly-graph-div {
    width: 100% !important;
    max-width: 950px !important;
    height: auto !important;
    margin: 20px auto;
    overflow: visible !important;
    page-break-inside: avoid !important;
}

/* Tablas Streamlit */
.stDataFrame, .stTable {
    width: 100% !important;
    max-width: 950px !important;
    margin: 15px auto;
    overflow: visible !important;
    page-break-inside: avoid !important;
}

/* Imágenes y SVG escalables */
img, svg {
    max-width: 100%;
    height: auto;
}

/* ===============================
   CONFIGURACIÓN PARA IMPRESIÓN
   =============================== */
@media print {
    html, body {
        width: 210mm;
        height: auto;
        zoom: 0.85;
        margin: 0;
        padding: 0;
        background: white;
    }

    @page {
        size: A4 portrait;
        margin: 1cm;
    }

    /* Evita cortes en elementos clave */
    .plotly-graph-div,
    .stDataFrame,
    .stTable {
        page-break-inside: avoid !important;
        break-inside: avoid-page !important;
        overflow: visible !important;
    }

    /* Oculta botones durante impresión */
    .print-button {
        display: none !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ===============================
# FUNCIÓN DE BOTÓN DE IMPRESIÓN STREAMLIT
# ===============================
def boton_imprimir_streamlit():
    st.markdown("""
        <div class="print-button" style="text-align: center; margin-top: 1rem;">
            <button onclick="window.print()" style="
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;">
                🖨️ Imprimir o Guardar como PDF
            </button>
        </div>
    """, unsafe_allow_html=True)


# ===============================
# SERVICIOS Y SIDEBAR
# ===============================
sld, sae = get_services()

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

# ===============================
# MOSTRAR ANÁLISIS GUARDADO
# ===============================
if 'df_actual' in st.session_state:
    st.subheader(f"Mostrando análisis: {st.session_state['analisis_actual']}")
    df_display = st.session_state['df_actual']
    if 'comentarios' in df_display.columns:
        df_display['longitud'] = df_display['comentarios'].str.len()
    else:
        df_display['longitud'] = 0

    show_comments_table(df_display)
    mostrar_graficos(df_display, color_discrete_map)
    show_export_button(df_display)
    boton_imprimir_streamlit()  # 🔹 Botón de impresión persistente


# ===============================
# SUBIR Y PROCESAR NUEVO ARCHIVO
# ===============================
archivo = upload_file_view()
if archivo:
    datos, mensaje, valido = process_uploaded_file(archivo, sld, sae)

    if valido:
        st.sidebar.success(mensaje)
        df = datos
        if df is not None and not df.empty:
            show_comments_table(df)
            mostrar_graficos(df, color_discrete_map)
            show_export_button(df)
            boton_imprimir_streamlit()  # 🔹 Botón de impresión persistente

            if st.button("Guardar Resultados"):
                file_name_base = archivo.name.split('.')[0]
                table_name = f"analisis_{file_name_base}"
                guardado_exitoso, mensaje_guardado = sae.guardar_analisis(
                    df, file_name_base, table_name
                )
                if guardado_exitoso:
                    st.success("Resultados guardados exitosamente.")
                    st.info(mensaje_guardado)
                    st.rerun()
                else:
                    st.error("Error al guardar los resultados.")
                    st.warning(mensaje_guardado)
        elif df is not None and df.empty:
            st.warning("El archivo se procesó, pero no se encontraron comentarios válidos después de la limpieza.")
        else:
            st.warning("No se pudieron cargar los datos correctamente.")
    else:
        st.sidebar.error(mensaje)
