import google.generativeai as genai
import pandas as pd
from use_cases.ports.ai_advisor import IAIAdvisor

class GeminiAdvisorAdapter(IAIAdvisor):
    def __init__(self, api_key: str):
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None

    def analyze_detractors(self, df: pd.DataFrame) -> str:
        if not self.model:
            return "Error: API Key de Gemini no configurada."

        # Filtramos detractores (Ajusta la lógica si usas escala 0-10)
        # Asumiendo que 'Clasificacion' o 'calificacion' existen
        if 'calificacion' in df.columns:
            detractors = df[df['calificacion'] <= 6]['comentarios'].dropna().tolist()
        else:
            return "No se encontró columna de calificación."

        if not detractors:
            return "¡Excelente trabajo! No se detectaron suficientes comentarios negativos para generar recomendaciones críticas."

        # Muestra limitada para no saturar tokens
        comments_text = "\n- ".join(detractors[:40])

        prompt = f"""
        Actúa como consultor experto en Customer Experience. Analiza estos comentarios negativos:
        {comments_text}

        Genera de 3 a 6 sugerencias de mejora estratégicas  y accionables para el negocio. Pero no me des ninguna adulación ni tu prompt inicial, sólo las sugerencias.
        Formato:
        1. **[Problema Detectado]**: [Sugerencia concreta]
        2. ...
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error al consultar Gemini: {str(e)}"