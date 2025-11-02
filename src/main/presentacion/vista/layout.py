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

    bins = list(range(0, int(df['longitud'].max()) + 50, 50))
    df['rango_longitud'] = pd.cut(df['longitud'], bins=bins, right=False)
    distribucion = df.groupby(['Clasificacion', 'rango_longitud']).size().reset_index(name='conteo')

    #Corregir el rango
    if pd.api.types.is_interval_dtype(distribucion['rango_longitud']):
        distribucion[['min', 'max']] = distribucion['rango_longitud'].apply(lambda x: pd.Series([x.left, x.right]))
    else:
        distribucion[['min', 'max']] = distribucion['rango_longitud'].astype(str).str.extract(r'(\d+\.?\d*),\s*(\d+\.?\d*)').astype(float)
    distribucion.drop(columns='rango_longitud', inplace=True)

    #Boton de exportar a Excel
    st.markdown("---")
    st.subheader("Exportar resultados")

    excel_bytes = generar_excel(df, resumen, distribucion)
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