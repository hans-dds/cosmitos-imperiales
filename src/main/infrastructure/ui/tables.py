import streamlit as st


def show_comments_table(df):
    """Muestra una tabla filtrable de comentarios."""
    st.subheader("Comentarios Filtrados")
    if 'Clasificacion' not in df.columns:
        st.warning("No hay datos de clasificación para mostrar.")
        return

    categories = ['Todas'] + sorted(
        df['Clasificacion'].dropna().unique().tolist())
    selected_category = st.selectbox("Filtrar por categoría", categories)

    if selected_category != 'Todas':
        df = df[df['Clasificacion'] == selected_category]

    number_of_comments = st.slider(
        "Número de comentarios a mostrar",
        min_value=10,
        max_value=len(df),
        value=10)

    st.dataframe(
        df[['calificacion', 'comentarios', 'Clasificacion']].head(
            number_of_comments),
        use_container_width=True
    )
