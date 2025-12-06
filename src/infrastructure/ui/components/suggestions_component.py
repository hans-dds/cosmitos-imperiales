import streamlit as st
import pandas as pd
from use_cases.generate_suggestions_use_case import GenerateSuggestionsUseCase


class SuggestionsComponent:
    def __init__(self, use_case: GenerateSuggestionsUseCase):
        self._use_case = use_case

    def render(self, df: pd.DataFrame):
        st.markdown("---")
        st.subheader("Sugerencias de Mejora (IA)")

        if st.button("Generar Recomendaciones Estratégicas", type="primary"):
            with st.spinner("Analizando comentarios de detractores..."):
                try:
                    suggestions = self._use_case.execute(df)

                    if not suggestions:
                        st.success(
                            "✅ No se han identificado áreas críticas de mejora en este período."
                        )
                    else:
                        cols = st.columns(len(suggestions))
                        for i, item in enumerate(suggestions):
                            with cols[i]:
                                st.error(f"Problema: {item['tema']}")
                                st.info(f"💡 {item['sugerencia']}")

                except Exception as e:
                    st.error(f"Error en análisis: {e}")
