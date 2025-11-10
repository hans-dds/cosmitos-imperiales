import streamlit as st
from negocio.sugerencias import analizar_comentarios

def mostrar_sugerencias(df):
    st.markdown("## 💡 Sugerencias de Mejora")

    if df is None or df.empty or "comentarios" not in df.columns:
        st.info("No se han identificado áreas críticas de mejora en este período.")
        return

    sugerencias = analizar_comentarios(df)

    if not sugerencias:
        st.success("No se han identificado áreas críticas de mejora en este período.")
        return

    for s in sugerencias:
        st.markdown(f"### 🔸 {s['tema']}")
        st.write(f"{s['sugerencia']}")
        st.divider()
