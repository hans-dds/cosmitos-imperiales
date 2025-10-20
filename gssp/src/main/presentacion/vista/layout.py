import streamlit as st

def mostrar_header():
    st.title("Gestor de Satisfacción y Seguimiento de Posventa")

def mostrar_tablas(df):
    columnas_requeridas = {'Clasificacion', 'comentarios', 'calificacion', 'longitud'}
    if not columnas_requeridas.issubset(df.columns):
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
