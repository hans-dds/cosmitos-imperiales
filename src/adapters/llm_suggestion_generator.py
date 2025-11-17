import os
import json
from typing import List
import httpx # O usa la librería 'openai' si la tienes

from use_cases.ports.suggestion_generator import ISuggestionGenerator
from domain.entities.suggestion import Suggestion

# Constante para el prompt
SUGGESTION_PROMPT_TEMPLATE = """
Analiza la siguiente lista de comentarios de clientes detractores de un concesionario de coches.
Identifica los 3 temas negativos más recurrentes y, para cada uno, genera una recomendación o sugerencia de mejora clara y accionable.

Reglas de respuesta:
1. Responde SÓLO con un objeto JSON válido.
2. El JSON debe ser una lista de objetos.
3. Cada objeto debe tener dos claves: "theme" (el tema negativo) y "recommendation" (la sugerencia).
4. No incluyas nada antes o después del JSON.
5. Si no hay comentarios o no se pueden identificar temas, devuelve una lista JSON vacía [].

Comentarios de detractores:
{comments}

Respuesta JSON:
"""


class LLMSuggestionGenerator(ISuggestionGenerator):
    """
    Implementación de ISuggestionGenerator que usa una API de LLM (ej. OpenAI).
    
    NOTA: Esto es un ejemplo. Adapta la URL y el 'Authorization' a tu
    proveedor de LLM (OpenAI, Azure, Gemini, etc.).
    """
    
    def __init__(self, api_key: str, api_url: str):
        self._api_key = api_key
        self._api_url = api_url 
        self._client = httpx.Client(
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json"
            },
            timeout=90.0
        )

    def generate_suggestions(self, comments: List[str]) -> List[Suggestion]:
        
        # Unir comentarios para el prompt
        comments_text = "\\n- ".join(comments)
        prompt = SUGGESTION_PROMPT_TEMPLATE.format(comments=comments_text)
        
        # Datos para la API
        payload = {
            "model": "gpt-4o-mini", 
            "messages": [
                {"role": "system", "content": "Eres un asistente de análisis de negocio."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2
        }

        try:
            response = self._client.post(self._api_url, json=payload)
            response.raise_for_status() # Error si la API falla
            
            # Extraer el contenido JSON de la respuesta
            json_text = response.json()['choices'][0]['message']['content']
            suggestions_data = json.loads(json_text)

            # Convertir el JSON a entidades de Dominio
            suggestions = [
                Suggestion(
                    theme=item.get('theme', 'Error de Tema'),
                    recommendation=item.get('recommendation', 'Error de Sugerencia')
                )
                for item in suggestions_data
            ]
            return suggestions

        except httpx.HTTPStatusError as e:
            print(f"Error de API de LLM (HTTP): {e.response.status_code} - {e.response.text}")
            return []
        except (json.JSONDecodeError, KeyError, Exception) as e:
            print(f"Error al generar o parsear sugerencias del LLM: {e}")
            return []
