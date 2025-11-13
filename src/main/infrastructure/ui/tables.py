import streamlit as st


def show_comments_table(df):
    """Displays a filterable table of comments."""
    st.subheader("Comentarios Filtrados")
    if 'Clasificacion' not in df.columns:
        st.warning("No classification data to display.")
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
