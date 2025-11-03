import pandas as pd
import streamlit as st
from presentacion.logica.exportador_excel import generar_excel

def show_header():
    st.title("Gestor de Satisfacción y Seguimiento de Posventa")

def show_tables(df):
    required_columns = {'Clasificacion', 'comentarios', 'calificacion', 'longitud'}

    if not required_columns.issubset(df.columns):
        st.error("El DataFrame no contiene las columnas necesarias para mostrar las tablas.")
        return

    st.subheader("Comentarios relevantes por categoría")

    categorias = ['Detractor', 'Neutro', 'Promotor']

    for categoria in categorias:
        st.markdown(f"#### {categoria}")

        top10 = (
            df[df['Clasificacion'] == categoria]
            .sort_values(by='longitud', ascending=False)
            .head(10)
        )

        st.dataframe(
            top10[['calificacion', 'comentarios']],
            use_container_width=True,
            hide_index=True
        )

    #Agregaciones
    resumen = df.groupby('Clasificacion').agg({
        'comentarios': 'count',
        'longitud': 'mean'
    }).reset_index().rename(columns={'comentarios': 'NumComentarios', 'longitud': 'LongitudPromedio'})

    resumen['Porcentaje'] = (resumen['NumComentarios'] / resumen['NumComentarios'].sum()) * 100

    #Boton de exportar a Excel
    st.markdown("---")
    st.subheader("Exportar resultados")

    excel_bytes = generar_excel(df, resumen)
    st.download_button(
        label="📎 Descargar reporte Excel con gráficas",
        data=excel_bytes,
        file_name="reporte_comentarios.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_excel_full"
    )

def upload_file_view():
    st.sidebar.header("📁 Cargar archivo")
    archivo = st.sidebar.file_uploader("Sube un archivo CSV o Excel", type=["csv", "xlsx"])
    return archivo


def show_comments_table(df):
    """
    Muestra una tabla filtrable por clase con un selector y un slider para
    controlar cuántos comentarios se muestran.

    Requisitos del DataFrame: columnas 'Clasificacion', 'comentarios', 'calificacion', 'longitud'
    """
    required_columns = {'Clasificacion', 'comentarios', 'calificacion', 'longitud'}

    if not required_columns.issubset(df.columns):
        st.error("El DataFrame no contiene las columnas necesarias para mostrar la tabla de comentarios filtrados.")
        return

    st.subheader("Tabla de comentarios filtrados")

    # Obtener clases disponibles (sin valores nulos)
    clases = [c for c in sorted(df['Clasificacion'].dropna().unique().tolist())]
    opciones = ['Todas'] + clases

    clase_seleccionada = st.selectbox("Seleccionar clase", opciones, index=0, help="Filtra los comentarios por la clase seleccionada")

    max_comentarios = int(df.shape[0]) if df.shape[0] > 0 else 10
    default_show = min(10, max_comentarios)
    cantidad = st.slider("Cantidad de comentarios a mostrar", min_value=10, max_value=max(10, max_comentarios), value=default_show, step=10)

    if clase_seleccionada == 'Todas':
        df_filtrado = df.copy()
    else:
        df_filtrado = df[df['Clasificacion'] == clase_seleccionada]

    # Ordenar por longitud (más largos primero) y limitar según slider
    df_mostrar = (
        df_filtrado.sort_values(by='longitud', ascending=False)
        .head(cantidad)
    )

    if df_mostrar.empty:
        st.info("No hay comentarios para la selección actual.")
        return

    st.dataframe(
        df_mostrar[['calificacion', 'comentarios', 'Clasificacion']].rename(columns={'calificacion': 'Calificación', 'comentarios': 'Comentario', 'Clasificacion': 'Clasificación'}),
        use_container_width=True,
        hide_index=True
    )


def show_export_button(df):
    """
    Muestra el botón de exportación a Excel con los datos completos del análisis.
    
    Requisitos del DataFrame: columnas 'Clasificacion', 'comentarios', 'calificacion', 'longitud'
    """
    required_columns = {'Clasificacion', 'comentarios', 'calificacion', 'longitud'}

    if not required_columns.issubset(df.columns):
        st.error("El DataFrame no contiene las columnas necesarias para la exportación.")
        return

    # Agregaciones
    resumen = df.groupby('Clasificacion').agg({
        'comentarios': 'count',
        'longitud': 'mean'
    }).reset_index().rename(columns={'comentarios': 'NumComentarios', 'longitud': 'LongitudPromedio'})

    resumen['Porcentaje'] = (resumen['NumComentarios'] / resumen['NumComentarios'].sum()) * 100

    bins = list(range(0, int(df['longitud'].max()) + 50, 50))
    df_temp = df.copy()
    df_temp['rango_longitud'] = pd.cut(df_temp['longitud'], bins=bins, right=False)
    distribucion = df_temp.groupby(['Clasificacion', 'rango_longitud']).size().reset_index(name='conteo')

    # Corregir el rango - convertir a string y extraer valores con regex
    distribucion['rango_str'] = distribucion['rango_longitud'].astype(str)
    # Extraer los números del formato "[0, 50)" o similar
    extracted = distribucion['rango_str'].str.extract(r'\[(\d+\.?\d*),\s*(\d+\.?\d*)\)')
    distribucion['min'] = extracted[0].astype(float)
    distribucion['max'] = extracted[1].astype(float)
    distribucion.drop(columns=['rango_longitud', 'rango_str'], inplace=True)

    # Botón de exportar a Excel
    st.markdown("---")
    st.subheader("Exportar resultados")

    excel_bytes = generar_excel(df, resumen, distribucion)
    st.download_button(
        label="📎 Descargar reporte Excel con gráficas",
        data=excel_bytes,
        file_name="reporte_comentarios.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_excel_export"
    )
