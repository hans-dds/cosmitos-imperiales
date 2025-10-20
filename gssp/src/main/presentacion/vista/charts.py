import plotly.express as px
import streamlit as st

def mostrar_graficos(df, color_discrete_map):
    # Validar que las columnas necesarias existen
    if 'Clasificacion' not in df.columns or 'comentarios' not in df.columns:
        st.error("El DataFrame no contiene las columnas necesarias ('Clasificacion' y 'comentarios') para mostrar los gráficos.")
        return

    # Crear columna 'longitud' si no existe
    if 'longitud' not in df.columns:
        df['longitud'] = df['comentarios'].apply(lambda x: len(str(x).split()))

    # Obtener conteo por clasificación
    conteo = df['Clasificacion'].value_counts().reset_index()
    conteo.columns = ['Clasificacion', 'cantidad']

    col1, col2 = st.columns(2)

    # Gráfico de pastel
    with col1:
        st.subheader("Distribución de comentarios")
        fig_pie = px.pie(
            conteo,
            names='Clasificacion',
            values='cantidad',
            color='Clasificacion',
            color_discrete_map=color_discrete_map,
            hole=0.4
        )
        # fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        # fig_pie.update_layout(
        #     showlegend=False,
        #     margin=dict(t=20, b=20, l=10, r=10)
        # )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Gráfico de barras
    with col2:
        st.subheader("Comentarios por categoría")
        fig_bar = px.bar(
            conteo,
            x='Clasificacion',
            y='cantidad',
            color='Clasificacion',
            text='cantidad',
            color_discrete_map=color_discrete_map
        )
        # fig_bar.update_layout(
        #     xaxis_title="Clasificación",
        #     yaxis_title="Cantidad",
        #     margin=dict(t=20, b=20, l=10, r=10),
        #     showlegend=False
        # )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Histograma
    st.subheader("¿Quiénes opinan más?")
    fig_hist = px.histogram(
        df,
        x='longitud',
        color='Clasificacion',
        nbins=15,
        barmode='overlay',
        opacity=0.8,
        title='Distribución de longitud de comentarios por categoría',
        labels={'longitud': 'Número de palabras'},
        color_discrete_map=color_discrete_map
    )
    fig_hist.update_layout(margin=dict(t=30, b=30, l=10, r=10))
    st.plotly_chart(fig_hist, use_container_width=True)
