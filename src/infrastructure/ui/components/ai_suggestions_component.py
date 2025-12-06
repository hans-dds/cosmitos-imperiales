import streamlit as st
import pandas as pd
from infrastructure.ui.controllers.streamlit_controller import (
    StreamlitController,
)


class AISuggestionsComponent:
    def render(self, controller: StreamlitController, df: pd.DataFrame):
        st.markdown("---")
        st.subheader("Sugerencias de Mejora (AI)")

        st.write("Analiza los comentarios negativos para generar estrategias.")

        if st.button("Generar Recomendaciones con IA"):
            with st.spinner("Consultando a Gemini..."):
                suggestions = controller.get_ai_suggestions(df)
                st.markdown(suggestions)
