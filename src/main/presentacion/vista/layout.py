import streamlit as st

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

def upload_file_view():
    st.sidebar.header("📁 Cargar archivo")
    archivo = st.sidebar.file_uploader("Sube un archivo CSV o Excel", type=["csv", "xlsx"])
    return archivo
