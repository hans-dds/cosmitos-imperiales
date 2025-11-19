"""
Constantes compartidas para la interfaz de usuario.
"""

# Opción especial que permite agregar todos los análisis guardados y
# verlos juntos.
ALL_ANALYSES_OPTION = "Todos los análisis"


def get_color_map() -> dict[str, str]:
    """
    Retorna el mapa de colores para las clasificaciones en la UI.
    Esta función está en la capa de infraestructura porque es configuración
    de presentación, no lógica de negocio.
    Returns:
        Diccionario que mapea clasificaciones a colores hexadecimales
    """
    return {
        'Promotor': '#00CC96',
        'Detractor': '#EF553B',
        'Neutro': '#636EFA'
    }
