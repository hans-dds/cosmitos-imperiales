import streamlit as st
import plotly.express as px


def show_charts(df, color_map):
    """Displays charts for the given DataFrame."""
    if 'Clasificacion' not in df.columns or 'comentarios' not in df.columns:
        st.error("DataFrame is missing required columns for charts.")
        return

    if 'longitud' not in df.columns:
        df['longitud'] = df['comentarios'].str.len()

    counts = df['Clasificacion'].value_counts().reset_index()
    counts.columns = ['Clasificacion', 'cantidad']

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Distribución de Sentimientos")
        fig_pie = px.pie(counts, names='Clasificacion', values='cantidad',
                         color='Clasificacion', color_discrete_map=color_map,
                         hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
    with col2:
        st.subheader("Comentarios por Categoría")
        fig_bar = px.bar(counts, x='Clasificacion', y='cantidad',
                         color='Clasificacion', text='cantidad',
                         color_discrete_map=color_map)
        st.plotly_chart(fig_bar, use_container_width=True)
