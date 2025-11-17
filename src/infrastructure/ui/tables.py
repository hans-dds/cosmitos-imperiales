import streamlit as st
import pandas as pd


def show_comments_table(df: pd.DataFrame):
    """
    Muestra una tabla filtrable de comentarios mostrando solo:
    - calificacion
    - comentarios
    - Clasificacion (Detractor, Neutro, Promotor)
    
    Args:
        df: DataFrame con las columnas requeridas
    """
    st.subheader("Comentarios Filtrados")
    
    # Validar que existan las columnas requeridas
    required_columns = ['calificacion', 'comentarios', 'Clasificacion']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.warning(f"No hay datos completos para mostrar. Faltan las columnas: {', '.join(missing_columns)}")
        return

    # Crear una copia del DataFrame con solo las columnas necesarias
    display_df = df[required_columns].copy()
    
    # Filtrar por categoría de clasificación
    categories = ['Todas'] + sorted(
        display_df['Clasificacion'].dropna().unique().tolist())
    selected_category = st.selectbox("Filtrar por categoría", categories)

    if selected_category != 'Todas':
        display_df = display_df[display_df['Clasificacion'] == selected_category]

    # Control de cantidad de comentarios a mostrar
    max_comments = max(10, len(display_df))
    number_of_comments = st.slider(
        "Número de comentarios a mostrar",
        min_value=10,
        max_value=max_comments,
        value=min(10, max_comments))

    # Mostrar la tabla con solo las columnas requeridas
    st.dataframe(
        display_df.head(number_of_comments),
        use_container_width=True,
        hide_index=True
    )
