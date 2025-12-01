from typing import List, Dict
from use_cases.ports.suggestion_generator import ISuggestionGenerator

class RuleBasedSuggestionAdapter(ISuggestionGenerator):
    def generate(self, comments: List[str]) -> List[Dict[str, str]]:
        if not comments:
            return []

        text = " ".join(comments).lower()
        suggestions = []

        # Reglas de negocio simulando análisis de IA
        if any(w in text for w in ['lento', 'tarda', 'espera', 'hora']):
            suggestions.append({
                "tema": "Optimización de Tiempos",
                "sugerencia": "Implementar notificaciones automáticas de estado para reducir la incertidumbre en sala de espera."
            })

        if any(w in text for w in ['actitud', 'grosero', 'atención', 'ignoro']):
            suggestions.append({
                "tema": "Calidad de Atención",
                "sugerencia": "Reforzar capacitación de habilidades blandas y protocolo de bienvenida para asesores."
            })
            
        if any(w in text for w in ['sucio', 'limpieza', 'mancha']):
            suggestions.append({
                "tema": "Control de Calidad",
                "sugerencia": "Establecer checklist de limpieza obligatorio verificado por supervisor antes de la entrega."
            })

        # Fallback si no hay suficientes temas específicos
        if len(suggestions) < 3:
             suggestions.append({
                "tema": "Seguimiento Post-Venta",
                "sugerencia": "Implementar llamada de cortesía a los 3 días para asegurar satisfacción con la reparación."
            })

        return suggestions[:3]