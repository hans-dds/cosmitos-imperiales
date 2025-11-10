import pandas as pd
import re
from collections import Counter

def analizar_comentarios(df):
    """
    Analiza los comentarios de clientes y genera sugerencias de mejora.
    Devuelve una lista de diccionarios con {'tema': ..., 'sugerencia': ...}
    """

    #Verificar que haya comentarios
    if df is None or 'comentarios' not in df.columns or df.empty:
        return []

    comentarios = df['comentarios'].dropna().tolist()

    #Detectar palabras o frases negativas comunes
    palabras_negativas = [
        "tarde", "malo", "caro", "deficiente", "lento",
        "error", "pésimo", "no funciona", "difícil", "problema",
        "queja", "retraso", "demora", "confuso", "mala atención"
    ]

    #Coincidencias
    temas_detectados = []
    for comentario in comentarios:
        for palabra in palabras_negativas:
            if re.search(rf"\b{palabra}\b", comentario.lower()):
                temas_detectados.append(palabra)

    #Obtener los 3 más frecuentes
    mas_frecuentes = [t for t, _ in Counter(temas_detectados).most_common(3)]

    if not mas_frecuentes:
        return []

    #Generar sugerencias simples
    sugerencias = []
    for tema in mas_frecuentes:
        if tema in ["tarde", "retraso", "demora", "lento"]:
            sugerencias.append({
                "tema": "Retrasos en el servicio",
                "sugerencia": "Revisar los tiempos de entrega y optimizar el proceso logístico."
            })
        elif tema in ["caro"]:
            sugerencias.append({
                "tema": "Precios elevados",
                "sugerencia": "Evaluar promociones o descuentos estratégicos para retener clientes sensibles al precio."
            })
        elif tema in ["mala atención", "pésimo", "deficiente"]:
            sugerencias.append({
                "tema": "Atención al cliente",
                "sugerencia": "Capacitar al personal y mejorar los canales de comunicación con los clientes."
            })
        elif tema in ["error", "no funciona"]:
            sugerencias.append({
                "tema": "Problemas técnicos",
                "sugerencia": "Monitorear y resolver errores frecuentes en la plataforma o los productos."
            })
        else:
            sugerencias.append({
                "tema": tema.capitalize(),
                "sugerencia": f"Investigar los motivos relacionados con '{tema}' para implementar mejoras."
            })

    return sugerencias
