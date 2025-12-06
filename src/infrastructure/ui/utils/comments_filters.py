"""Utilidades para aplicar los mismos filtros de la UI a los comentarios.

Centraliza la lógica que antes estaba duplicada en el componente de exportación
para poder reutilizarla también al generar adjuntos para envío por correo.
"""

from __future__ import annotations

from typing import Any
import pandas as pd


def apply_comments_filters(
    df: pd.DataFrame, session_state: Any
) -> pd.DataFrame:
    """Aplica filtros y ordenamientos configurados en la UI sobre el DataFrame.

    Reglas soportadas (todas opcionales y solo si existen las columnas):
    - Filtro por categoría: `comments_filter_category` (ignora "Todas")
    - Ordenamiento: `comments_sort_by` + `comments_sort_dir`
    - Límite de registros: `comments_filter_count`

    Args:
        df: DataFrame completo de comentarios.
        session_state: Objeto `st.session_state` (inyectado para facilitar pruebas).

    Returns:
        DataFrame filtrado/ordenado/limitado según configuración actual.
    """
    if df is None or df.empty:
        return df

    filtered = df.copy()

    sel_cat = getattr(session_state, "get", lambda *a, **k: None)(
        "comments_filter_category"
    )
    if sel_cat and sel_cat != "Todas" and "Clasificacion" in filtered.columns:
        filtered = filtered[filtered["Clasificacion"] == sel_cat]

    sort_by_label = getattr(session_state, "get", lambda *a, **k: None)(
        "comments_sort_by"
    )
    sort_dir_label = getattr(session_state, "get", lambda *a, **k: None)(
        "comments_sort_dir"
    )
    label_to_column = {
        "Calificación": "calificacion",
        "Clasificación": "Clasificacion",
        "Fiabilidad": "Fiabilidad",
    }
    if sort_by_label and sort_by_label != "Sin ordenar":
        col = label_to_column.get(sort_by_label)
        if col in filtered.columns:
            filtered = filtered.sort_values(
                by=col,
                ascending=(sort_dir_label == "Ascendente"),
                kind="mergesort",
            )

    sel_count = getattr(session_state, "get", lambda *a, **k: None)(
        "comments_filter_count"
    )
    if isinstance(sel_count, int) and sel_count > 0:
        filtered = filtered.head(sel_count)

    return filtered
