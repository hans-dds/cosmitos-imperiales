import streamlit as st
from controladores.loader import cargar_datos
# from src.main.presentacion.controladores.loader import cargar_datos
# from vista.preprocess import limpiar_datos, calcular_longitud
from vista.charts import mostrar_graficos
from vista.layout import mostrar_tablas, mostrar_header
from vista.utils import color_discrete_map



st.set_page_config(page_title="GSSP", layout="wide")

st.markdown("""
    <style>
        .stAppDeployButton { visibility: hidden; }
        #stDecoration {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.sidebar.header("📁 Cargar archivo")
archivo = st.sidebar.file_uploader("Sube un archivo CSV o Excel", type=["csv", "xlsx"])

mostrar_header()

if archivo:
    datos, mensaje, valido = cargar_datos(archivo)

    if valido:
        st.sidebar.success(mensaje)
        # Si es un dict (2 hojas), puedes combinar o usar la hoja que necesites
        # if isinstance(datos, dict):
            # df = datos['Encuesta salida']
        # else:
            # df = datos  # Para CSV

        df = datos
        st.subheader("Vista previa de datos")
        st.dataframe(df.head(5), use_container_width=True, hide_index=True)

        # df = limpiar_datos(df)
        # df = calcular_longitud(df)

        mostrar_graficos(df, color_discrete_map)
        mostrar_tablas(df)
    else:
        st.sidebar.error(mensaje)
