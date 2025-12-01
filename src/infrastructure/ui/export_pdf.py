"""Generación de PDF con resumen, visualizaciones y tabla de comentarios."""

from datetime import datetime
from io import BytesIO
from typing import Dict, Iterable, List, Tuple, TYPE_CHECKING

import pandas as pd
import plotly.express as px
import plotly.io as pio
from fpdf import FPDF

if TYPE_CHECKING:
    import plotly.graph_objs

from domain.services.metrics_calculator import (
    calculate_comment_length, calculate_summary_metrics)
from infrastructure.ui.constants import get_color_map

_MAX_COMMENTS = 15
_CHART_WIDTH = 165  # mm (ligeramente más pequeño para mejor ajuste)
_LINE_HEIGHT = 6

_COLOR_TABLE_HEADER_BG = (235, 240, 250)
_COLOR_TABLE_ROW_ALT_BG = (248, 248, 248)
_COLOR_TABLE_BORDER = (220, 220, 220)
_COLOR_TEXT_MUTED = (90, 90, 90)


class _ReportePDF(FPDF):
    """FPDF con cabecera y pie."""

    def __init__(self, titulo: str) -> None:
        super().__init__(orientation="P", unit="mm", format="A4")
        self.titulo = titulo

    def header(self) -> None:  # pragma: no cover
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, self.titulo, new_x="LMARGIN", new_y="NEXT",
                  align="C")
        self.set_draw_color(220, 220, 220)
        self.set_line_width(0.2)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(2)

    def footer(self) -> None:  # pragma: no cover
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")


def generate_pdf_export(
        df: pd.DataFrame,
        color_map: Dict[str, str] = None,
        comments_df: pd.DataFrame | None = None) -> bytes:
    """Crea y devuelve el PDF en bytes. Usa `color_map` si se provee.

    Si `comments_df` se especifica, la sección de comentarios usará ese
    subconjunto y orden en lugar de tomar los primeros registros.
    """
    if df is None or df.empty:
        raise ValueError(
            "El DataFrame está vacío. No se puede generar el PDF.")
    if color_map is None:
        color_map = get_color_map()
    try:
        datos = _preparar_dataframe(df)
        if datos.empty:
            raise ValueError("No hay datos válidos para generar el PDF.")
        pdf = _ReportePDF("Reporte de comentarios")
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        _render_resumen(pdf, datos)
        figuras = _crear_figuras(datos, color_map)
        if figuras:
            _render_charts(pdf, figuras)
        else:
            pdf.set_font("Helvetica", "I", 10)
            pdf.cell(0, 8, "No se pudieron generar las visualizaciones.",
                     new_x="LMARGIN", new_y="NEXT")
            pdf.ln(4)
        # Preparar selección de comentarios si se proporcionó
        comentarios_preparados = None
        if comments_df is not None and not comments_df.empty:
            comentarios_preparados = _preparar_dataframe(comments_df)
        _render_comments(pdf, comentarios_preparados if comentarios_preparados is not None else datos)
        contenido = pdf.output(dest="S")
        if not contenido or (
                isinstance(
                    contenido,
                    (str,
                     bytes,
                     bytearray)) and len(contenido) == 0):
            raise ValueError("El PDF generado está vacío.")
        if isinstance(contenido, str):
            return contenido.encode("latin-1")
        if isinstance(contenido, bytearray):
            return bytes(contenido)
        return contenido
    except Exception as e:
        pdf = _ReportePDF("Error al generar reporte")
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Error al generar el PDF",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 8, f"Ocurrió un error: {str(e)}")
        contenido = pdf.output(dest="S")
        if isinstance(contenido, str):
            return contenido.encode("latin-1")
        if isinstance(contenido, bytearray):
            return bytes(contenido)
        return contenido


def _preparar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza columnas y agrega métricas requeridas para el PDF."""
    datos = df.copy()
    # Asegurar columnas requeridas
    if "Clasificacion" not in datos.columns:
        datos["Clasificacion"] = "Sin Clasificación"
    datos["Clasificacion"] = datos["Clasificacion"].fillna("Sin Clasificación")
    if "comentarios" not in datos.columns:
        datos["comentarios"] = ""
    datos["comentarios"] = datos["comentarios"].fillna("")
    datos = calculate_comment_length(datos)
    if "num_palabras" not in datos.columns:
        datos["num_palabras"] = datos["comentarios"].astype(
            str).str.split().str.len()
    if "calificacion" not in datos.columns:
        datos["calificacion"] = "-"
    return datos


def _render_resumen(pdf: _ReportePDF, datos: pd.DataFrame) -> None:
    """Renderiza resumen y tabla por categoría."""
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"Total de comentarios analizados: {len(datos)}",
             new_x="LMARGIN", new_y="NEXT")
    pdf.cell(
        0,
        8,
        f"Fecha del reporte: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        new_x="LMARGIN",
        new_y="NEXT")
    pdf.ln(2)
    resumen = calculate_summary_metrics(datos)
    if resumen.empty:
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 8, "No hay datos suficientes para generar el resumen.",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)
        return
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Resumen por categoría", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(*_COLOR_TABLE_HEADER_BG)
    pdf.set_draw_color(*_COLOR_TABLE_BORDER)
    pdf.cell(60, _LINE_HEIGHT + 2, "Clasificación", border=1, fill=True)
    pdf.cell(40, _LINE_HEIGHT + 2, "Comentarios", border=1, fill=True, align="C")
    pdf.cell(50, _LINE_HEIGHT + 2, "Longitud promedio", border=1, fill=True, align="C")
    pdf.ln(_LINE_HEIGHT + 2)
    pdf.set_font("Helvetica", "", 10)
    for _, fila in resumen.iterrows():
        clasificacion = str(fila.get("Clasificacion", "Sin clasificación"))
        num_comentarios = int(fila.get("NumComentarios", 0))
        longitud_prom = float(fila.get("LongitudPromedio", 0))
        pdf.cell(60, _LINE_HEIGHT + 2, clasificacion, border=1)
        pdf.cell(40, _LINE_HEIGHT + 2, str(num_comentarios), border=1, align="C")
        pdf.cell(50, _LINE_HEIGHT + 2, f"{longitud_prom:.1f}", border=1, align="C")
        pdf.ln(_LINE_HEIGHT + 2)
    pdf.ln(4)


def _crear_figuras(
    datos: pd.DataFrame,
    color_map: Dict[str, str]
) -> List[Tuple[str, 'plotly.graph_objs.Figure']]:
    """Devuelve figuras Plotly a incluir en el PDF."""
    if datos.empty or "Clasificacion" not in datos.columns:
        return []
    clasificaciones_unicas = datos["Clasificacion"].dropna().unique()
    if len(clasificaciones_unicas) == 0:
        return []
    mapa_colores = _normalizar_color_map(color_map, clasificaciones_unicas)
    conteo = datos["Clasificacion"].value_counts().reset_index()
    conteo.columns = ["Clasificacion", "cantidad"]
    if conteo.empty:
        return []
    fig_pie = px.pie(
        conteo,
        names="Clasificacion",
        values="cantidad",
        color="Clasificacion",
        color_discrete_map=mapa_colores,
        hole=0.4,
        title="Distribución de comentarios",
    )
    fig_bar = px.bar(
        conteo,
        x="Clasificacion",
        y="cantidad",
        color="Clasificacion",
        text="cantidad",
        color_discrete_map=mapa_colores,
        title="Comentarios por categoría",
    )
    x_col = "num_palabras" if "num_palabras" in datos.columns else "longitud"
    x_label = "Número de palabras" if "num_palabras" in datos.columns \
        else "Número de caracteres"
    fig_hist = px.histogram(
        datos,
        x=x_col,
        color="Clasificacion",
        nbins=15,
        barmode="overlay",
        opacity=0.8,
        labels={x_col: x_label},
        color_discrete_map=mapa_colores,
        title="¿Quiénes opinan más?",
    )
    return [
        ("Distribución de comentarios", fig_pie),
        ("Comentarios por categoría", fig_bar),
        ("¿Quiénes opinan más?", fig_hist),
    ]


def _render_charts(
    pdf: _ReportePDF,
    figuras: Iterable[Tuple[str, 'plotly.graph_objs.Figure']]
) -> None:
    """Renderiza figuras como imágenes PNG."""
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Visualizaciones", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    for titulo, figura in figuras:
        try:
            imagen = BytesIO(
                pio.to_image(
                    figura,
                    format="png",
                    scale=2,
                    engine="kaleido"))
            imagen.seek(0)
            pdf.set_font("Helvetica", "I", 10)
            pdf.cell(0, 6, titulo, new_x="LMARGIN", new_y="NEXT")
            pdf.image(imagen, w=_CHART_WIDTH)
            pdf.ln(4)
        except Exception:
            pdf.set_font("Helvetica", "I", 10)
            pdf.cell(
                0,
                6,
                f"{titulo} (no disponible)",
                new_x="LMARGIN",
                new_y="NEXT")
            pdf.ln(4)


def _draw_comments_header(pdf: _ReportePDF, col1_w: float, col2_w: float, col3_w: float) -> None:
    """Dibuja el encabezado de la tabla de comentarios."""
    pdf.set_fill_color(*_COLOR_TABLE_HEADER_BG)
    pdf.set_draw_color(*_COLOR_TABLE_BORDER)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(col1_w, _LINE_HEIGHT + 2, "Clasificación", border=1, fill=True)
    pdf.cell(col2_w, _LINE_HEIGHT + 2, "Calificación", border=1, fill=True, align="C")
    pdf.cell(col3_w, _LINE_HEIGHT + 2, "Comentario", border=1, fill=True)
    pdf.ln(_LINE_HEIGHT + 2)


def _render_comments(pdf: _ReportePDF, datos: pd.DataFrame) -> None:
    """Renderiza la tabla de comentarios, con ajuste y salto de página."""
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Comentarios recientes", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    # Validar que hay datos
    if datos.empty:
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 8, "No hay comentarios para mostrar.", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)
        return
    seleccion = datos.head(_MAX_COMMENTS)
    if seleccion.empty:
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 8, "No hay comentarios para mostrar.", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)
        return

    col1_w = 40  # Clasificación
    col2_w = 25  # Calificación
    col3_w = (pdf.w - pdf.l_margin - pdf.r_margin) - col1_w - col2_w  # Comentario

    # Encabezado de tabla
    _draw_comments_header(pdf, col1_w, col2_w, col3_w)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    for idx, (_, fila) in enumerate(seleccion.iterrows()):
        clasificacion = str(fila.get('Clasificacion', 'Sin clasificación'))
        calificacion = str(fila.get('calificacion', '-'))
        comentario = str(fila.get('comentarios', '(Sin comentario)')).strip() or "(Sin comentario)"

        if idx % 2 == 1:
            pdf.set_fill_color(*_COLOR_TABLE_ROW_ALT_BG)
            fill_row = True
        else:
            fill_row = False

        comment_lines = _wrap_text_to_width(pdf, comentario, col3_w - 3)
        row_height = max(_LINE_HEIGHT + 2, _LINE_HEIGHT * max(1, len(comment_lines)))

        available = (pdf.h - pdf.b_margin) - pdf.get_y()
        if row_height > available:
            pdf.add_page()
            _draw_comments_header(pdf, col1_w, col2_w, col3_w)

        pdf.set_draw_color(*_COLOR_TABLE_BORDER)
        pdf.cell(col1_w, row_height, clasificacion, border=1, fill=fill_row)
        pdf.cell(col2_w, row_height, calificacion, border=1, align="C", fill=fill_row)

        x_before = pdf.get_x()
        y_before = pdf.get_y()
        pdf.set_draw_color(*_COLOR_TABLE_BORDER)
        if fill_row:
            pdf.set_fill_color(*_COLOR_TABLE_ROW_ALT_BG)
            pdf.rect(x_before, y_before, col3_w, row_height, style="FD")
        else:
            pdf.rect(x_before, y_before, col3_w, row_height, style="D")
        pdf.set_xy(x_before + 1.5, y_before + 1)
        for line in comment_lines:
            pdf.multi_cell(col3_w - 3, _LINE_HEIGHT - 1, line, border=0)
            # multi_cell resetea X al margen izquierdo, lo corregimos:
            pdf.set_x(x_before + 1.5)
        pdf.set_xy(pdf.l_margin, y_before + row_height)

    pdf.ln(2)


def _wrap_text_to_width(pdf: FPDF, text: str, width: float) -> List[str]:
    """Divide el texto en líneas que respetan el ancho indicado (mm)."""
    if not text:
        return [""]
    words = str(text).split()
    lines: List[str] = []
    current = ""
    for word in words:
        probe = f"{current} {word}".strip()
        if pdf.get_string_width(probe) <= width:
            current = probe
        else:
            if current:
                lines.append(current)
            # Si una palabra es más larga que el ancho, cortarla de forma segura
            if pdf.get_string_width(word) > width:
                chunk = ""
                for ch in word:
                    if pdf.get_string_width(chunk + ch) <= width:
                        chunk += ch
                    else:
                        lines.append(chunk)
                        chunk = ch
                current = chunk
            else:
                current = word
    if current:
        lines.append(current)
    return lines


def _normalizar_color_map(
    color_discrete_map: Dict[str, str],
    categorias: Iterable[str]
) -> Dict[str, str]:
    """
    Normaliza el mapa de colores para manejar diferentes variaciones de
    texto.
    Args:
        color_discrete_map: Mapa de colores original
        categorias: Categorías encontradas en los datos
    Returns:
        Mapa de colores normalizado
    """
    mapa = {}
    # Agregar variaciones de cada clave del mapa original
    for clave, valor in color_discrete_map.items():
        mapa[clave] = valor
        mapa[clave.lower()] = valor
        mapa[clave.upper()] = valor
        mapa[clave.capitalize()] = valor
    # Asegurar que todas las categorías tengan un color asignado
    for categoria in categorias:
        if categoria not in mapa:
            clave = str(categoria).lower()
            # Buscar en el mapa original con diferentes variaciones
            for key in color_discrete_map.keys():
                if key.lower() == clave:
                    mapa[categoria] = color_discrete_map[key]
                    break
            else:
                # Color por defecto si no se encuentra
                mapa[categoria] = "#808080"
    return mapa
