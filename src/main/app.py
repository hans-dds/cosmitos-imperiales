import pandas as pd
import streamlit as st
import os

from presentacion.vista.charts import mostrar_graficos
from presentacion.controlador.loader import get_services, process_uploaded_file
from presentacion.vista.layout import show_header, show_tables, upload_file_view
import presentacion.vista.config_app_ui as cau
from presentacion.vista.utils import color_discrete_map

# 🔹 Nuevo: Importar funciones para exportar/descargar PDF
from negocio.ServicioDescargaPDF import boton_descargar_pdf


# --- Configuración inicial de la página ---
cau.config_page()
show_header()

# --- 🔹 Inyectar CSS global para ajustar tamaño de gráficas y evitar cortes al imprimir ---
st.markdown("""
<style>
/* ===============================
   AJUSTES DE VISUALIZACIÓN GLOBAL
   =============================== */

html, body {
    width: 100%;
    max-width: 100%;
    overflow-x: hidden !important;
    margin: 0;
    padding: 0;
    zoom: 1.0;
}

/* Contenedor principal centrado */
.block-container {
    max-width: 95vw !important;
    margin: auto;
    padding: 1rem;
}

/* ===============================
   ESTILO DE GRÁFICAS PLOTLY
   =============================== */
.plotly-graph-div {
    width: 100% !important;
    max-width: 950px !important;
    height: auto !important;
    margin: 20px auto !important;
    overflow: visible !important;
    page-break-inside: avoid !important;
}

.js-plotly-plot, .plot-container, .svg-container {
    page-break-inside: avoid !important;
    overflow: visible !important;
}

/* ===============================
   TABLAS Y DATAFRAMES
   =============================== */
.dataframe, .stDataFrame, .stTable {
    width: 100% !important;
    max-width: 100% !important;
    overflow: visible !important;
    page-break-inside: avoid !important;
    margin-bottom: 20px;
}

table {
    border-collapse: collapse !important;
    width: 100% !important;
    font-size: 0.9rem;
}

table, th, td {
    border: 1px solid #ddd !important;
    padding: 6px !important;
}

/* ===============================
   CONFIGURACIÓN PARA IMPRESIÓN
   =============================== */
@media print {
    html, body {
        width: 210mm;
        height: auto;
        zoom: 0.9;
        background: white !important;
        -webkit-print-color-adjust: exact !important;
    }

    @page {
        size: A4 portrait;
        margin: 1cm;
    }

    .plotly-graph-div, .js-plotly-plot, .stDataFrame, .stTable, table {
        page-break-inside: avoid !important;
        break-inside: avoid-page !important;
    }

    h1, h2, h3 {
        page-break-after: avoid;
    }

    .main, .block-container {
        overflow: visible !important;
    }

    /* Ocultar botones en modo impresión */
    .no-print {
        display: none !important;
    }
}
</style>
""", unsafe_allow_html=True)


# --- Inicializar servicios ---
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

# --- Vista principal ---
st.title("Análisis de Sentimientos")

# 🔹 Botón de impresión funcional en Streamlit
st.markdown(
    """
    <div class="no-print" style="text-align:right; margin-top:-40px;">
        <button onclick="window.print()" 
                style="background-color:#0099ff;color:white;border:none;
                       padding:8px 16px;border-radius:6px;cursor:pointer;">
            🖨️ Imprimir reporte
        </button>
    </div>
    """,
    unsafe_allow_html=True
)

# Mostrar análisis cargado desde el sidebar
if 'df_actual' in st.session_state:
    st.subheader(f"Mostrando análisis: {st.session_state['analisis_actual']}")
    df_display = st.session_state['df_actual']

    if 'comentarios' in df_display.columns:
        df_display['longitud'] = df_display['comentarios'].str.len()
    else:
        df_display['longitud'] = 0

    mostrar_graficos(df_display, color_discrete_map)
    show_tables(df_display)

    # 🔹 Botones de exportación PDF
    html_reporte = df_display.to_html(index=False)
    html_reporte = f"""
    <h1>Informe de análisis de sentimientos</h1>
    <p>Este informe fue generado automáticamente por la aplicación Streamlit.</p>
    {html_reporte}
    """
    st.markdown("### 📤 Opciones de exportación del análisis cargado")
    boton_descargar_pdf(html_reporte, nombre_archivo="informe_sentimientos.pdf")

st.markdown("---")

# --- Carga de archivo nuevo ---
archivo = upload_file_view()
if archivo:
    datos, mensaje, valido = process_uploaded_file(archivo, sld, sae)

    if valido:
        st.sidebar.success(mensaje)
        st.subheader("Resultados del Nuevo Análisis")
        df = datos

        if df is not None and not df.empty:
            st.dataframe(df.head(5), use_container_width=True, hide_index=True)

            if st.button("Guardar Resultados"):
                file_name_base = archivo.name.split('.')[0]
                table_name = f"analisis_{file_name_base}"
                guardado_exitoso, mensaje_guardado = sae.guardar_analisis(
                    df, file_name_base, table_name
                )
                if guardado_exitoso:
                    st.success("Resultados guardados exitosamente.")
                    st.info(mensaje_guardado)
                    st.experimental_rerun()
                else:
                    st.error("Error al guardar los resultados.")
                    st.warning(mensaje_guardado)

            mostrar_graficos(df, color_discrete_map)
            show_tables(df)

            html_reporte = df.to_html(index=False)
            html_reporte = f"""
            <h1>Informe de análisis de sentimientos</h1>
            <p>Este informe fue generado automáticamente por la aplicación Streamlit.</p>
            {html_reporte}
            """
            st.markdown("### 📤 Opciones de exportación del nuevo análisis")
            boton_descargar_pdf(html_reporte, nombre_archivo="informe_sentimientos.pdf")

        elif df is not None and df.empty:
            st.warning("El archivo se procesó, pero no se encontraron comentarios válidos.")
        else:
            st.warning("No se pudieron cargar los datos correctamente.")
    else:
        st.sidebar.error(mensaje)
