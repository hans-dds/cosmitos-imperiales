"""Generación de PDF con resumen, visualizaciones y tabla de comentarios."""

from datetime import datetime
import math
from io import BytesIO
from typing import Dict, Iterable, List, Tuple, TYPE_CHECKING

import pandas as pd
import plotly.express as px
import plotly.io as pio
from fpdf import FPDF
from infrastructure.ui.utils.text import to_pdf_compatible as _to_pdf_compatible, normalize_newlines as _norm_newlines

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
        self.cell(0, 10, _to_pdf_compatible(self.titulo), new_x="LMARGIN", new_y="NEXT",
                  align="C")
        self.set_draw_color(220, 220, 220)
        self.set_line_width(0.2)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(2)

    def footer(self) -> None:  # pragma: no cover
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, _to_pdf_compatible(f"Página {self.page_no()}"), align="C")


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
        shown_count = None
        if comments_df is not None and not comments_df.empty:
            comentarios_preparados = _preparar_dataframe(comments_df)
            shown_count = len(comentarios_preparados)
        else:
            shown_count = min(len(datos), _MAX_COMMENTS)
        _render_comments(pdf, comentarios_preparados if comentarios_preparados is not None else datos.head(_MAX_COMMENTS), shown_count=shown_count)
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
        pdf.cell(0, 10, _to_pdf_compatible("Error al generar el PDF"),
                 new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 8, _to_pdf_compatible(f"Ocurrió un error: {str(e)}"))
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
    pdf.cell(0, 8, _to_pdf_compatible(f"Total de comentarios analizados: {len(datos)}"),
             new_x="LMARGIN", new_y="NEXT")
    pdf.cell(
        0,
        8,
        _to_pdf_compatible(f"Fecha del reporte: {datetime.now().strftime('%d/%m/%Y %H:%M')}"),
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
    pdf.cell(0, 8, _to_pdf_compatible("Resumen por categoría"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(*_COLOR_TABLE_HEADER_BG)
    pdf.set_draw_color(*_COLOR_TABLE_BORDER)
    pdf.cell(60, _LINE_HEIGHT + 2, _to_pdf_compatible("Clasificación"), border=1, fill=True)
    pdf.cell(40, _LINE_HEIGHT + 2, _to_pdf_compatible("Comentarios"), border=1, fill=True, align="C")
    pdf.cell(50, _LINE_HEIGHT + 2, _to_pdf_compatible("Longitud promedio"), border=1, fill=True, align="C")
    pdf.ln(_LINE_HEIGHT + 2)
    pdf.set_font("Helvetica", "", 10)
    for _, fila in resumen.iterrows():
        clasificacion = _to_pdf_compatible(str(fila.get("Clasificacion", "Sin clasificación")))
        num_comentarios = int(fila.get("NumComentarios", 0))
        longitud_prom = float(fila.get("LongitudPromedio", 0))
        pdf.cell(60, _LINE_HEIGHT + 2, clasificacion, border=1)
        pdf.cell(40, _LINE_HEIGHT + 2, _to_pdf_compatible(str(num_comentarios)), border=1, align="C")
        pdf.cell(50, _LINE_HEIGHT + 2, _to_pdf_compatible(f"{longitud_prom:.1f}"), border=1, align="C")
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
    pdf.cell(0, 8, _to_pdf_compatible("Visualizaciones"), new_x="LMARGIN", new_y="NEXT")
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
            pdf.cell(0, 6, _to_pdf_compatible(titulo), new_x="LMARGIN", new_y="NEXT")
            pdf.image(imagen, w=_CHART_WIDTH)
            pdf.ln(4)
        except Exception:
            pdf.set_font("Helvetica", "I", 10)
            pdf.cell(
                0,
                6,
                _to_pdf_compatible(f"{titulo} (no disponible)"),
                new_x="LMARGIN",
                new_y="NEXT")
            pdf.ln(4)


def _draw_comments_header(pdf: _ReportePDF, col1_w: float, col2_w: float, col3_w: float) -> None:
    """Dibuja el encabezado de la tabla de comentarios."""
    pdf.set_fill_color(*_COLOR_TABLE_HEADER_BG)
    pdf.set_draw_color(*_COLOR_TABLE_BORDER)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(col1_w, _LINE_HEIGHT + 2, _to_pdf_compatible("Clasificación"), border=1, fill=True)
    pdf.cell(col2_w, _LINE_HEIGHT + 2, _to_pdf_compatible("Calificación"), border=1, fill=True, align="C")
    pdf.cell(col3_w, _LINE_HEIGHT + 2, _to_pdf_compatible("Comentario"), border=1, fill=True)
    pdf.ln(_LINE_HEIGHT + 2)
    # Evitar que el color de relleno del header se herede a filas de datos
    pdf.set_fill_color(255, 255, 255)


def _render_comments(pdf: _ReportePDF, datos: pd.DataFrame, shown_count: int | None = None) -> None:
    """Renderiza la tabla de comentarios, con ajuste y salto de página.

    shown_count: si se proporciona, se mostrará una leyenda con la cantidad.
    """
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, _to_pdf_compatible("Comentarios recientes"), new_x="LMARGIN", new_y="NEXT")
    if shown_count is not None:
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(*_COLOR_TEXT_MUTED)
        pdf.cell(0, 6, _to_pdf_compatible(f"Mostrando {shown_count} comentario(s)"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
    pdf.ln(1)
    # Validar que hay datos
    if datos.empty:
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 8, _to_pdf_compatible("No hay comentarios para mostrar."), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)
        return
    seleccion = datos
    if seleccion.empty:
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 8, _to_pdf_compatible("No hay comentarios para mostrar."), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)
        return

    col1_w = 38  # Clasificación (ligero ajuste para más espacio a comentario)
    col2_w = 24  # Calificación
    col3_w = (pdf.w - pdf.l_margin - pdf.r_margin) - col1_w - col2_w  # Comentario

    # Encabezado de tabla
    _draw_comments_header(pdf, col1_w, col2_w, col3_w)

    pdf.set_font("Helvetica", "", 10)  # Asegurar texto normal (no bold)
    pdf.set_text_color(0, 0, 0)
    for idx, (_, fila) in enumerate(seleccion.iterrows()):
        clasificacion = _to_pdf_compatible(str(fila.get('Clasificacion', 'Sin clasificación')))
        calificacion = _to_pdf_compatible(str(fila.get('calificacion', '-')))
        raw_comment = str(fila.get('comentarios', '(Sin comentario)')).strip() or "(Sin comentario)"
        comentario = _to_pdf_compatible(_norm_newlines(raw_comment))

        if idx % 2 == 1:
            pdf.set_fill_color(*_COLOR_TABLE_ROW_ALT_BG)
            fill_row = True
        else:
            fill_row = False

        padding_x = 1.5
        padding_y = 1.0
        line_h = _LINE_HEIGHT
        text_w = col3_w - 2 * padding_x
        comment_lines = _wrap_text_to_width(pdf, comentario, text_w)
        # Estimar líneas por longitud de caracteres (sin holgura fija)
        n_est_by_chars = _estimate_lines_by_chars(pdf, comentario, text_w, line_h)
        # Holgura adaptativa: solo si la última línea va muy llena
        if comment_lines:
            last_line = comment_lines[-1]
            last_ratio = (pdf.get_string_width(last_line) / text_w) if text_w > 0 else 0
            adaptive_slack = 1 if last_ratio > 0.9 else 0
        else:
            adaptive_slack = 0
        n_lines = max(1, len(comment_lines) + adaptive_slack, n_est_by_chars)
        text_h_total = line_h * n_lines
        safety_margin = 0.6  # mm de holgura para evitar traslapes por redondeo
        row_height = max(line_h + 2, text_h_total + 2 * padding_y + safety_margin)

        available = (pdf.h - pdf.b_margin) - pdf.get_y()
        if row_height > available:
            pdf.add_page()
            _draw_comments_header(pdf, col1_w, col2_w, col3_w)

        pdf.set_draw_color(*_COLOR_TABLE_BORDER)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(col1_w, row_height, _to_pdf_compatible(clasificacion), border=1, fill=fill_row)
        pdf.cell(col2_w, row_height, _to_pdf_compatible(calificacion), border=1, align="C", fill=fill_row)

        x_before = pdf.get_x()
        y_before = pdf.get_y()
        pdf.set_draw_color(*_COLOR_TABLE_BORDER)
        if fill_row:
            pdf.set_fill_color(*_COLOR_TABLE_ROW_ALT_BG)
            pdf.rect(x_before, y_before, col3_w, row_height, style="FD")
        else:
            pdf.rect(x_before, y_before, col3_w, row_height, style="D")
        pdf.set_xy(x_before + padding_x, y_before + padding_y)
        pdf.set_font("Helvetica", "", 10)  # forzar texto normal en comentario
        for i, line in enumerate(comment_lines):
            # Última línea: evitar agregar espacio innecesario
            pdf.multi_cell(text_w, line_h, _to_pdf_compatible(line), border=0)
            # multi_cell resetea X al margen izquierdo, lo corregimos:
            if i < n_lines - 1:
                pdf.set_x(x_before + padding_x)
        pdf.set_xy(pdf.l_margin, y_before + row_height)

    pdf.ln(2)


def _wrap_text_to_width(pdf: FPDF, text: str, width: float) -> List[str]:
    """Divide el texto en líneas que respetan el ancho indicado (mm)."""
    if not text:
        return [""]
    base = _to_pdf_compatible(_norm_newlines(str(text)))
    words = base.split()
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
 

def _estimate_lines_by_chars(pdf: FPDF, text: str, width: float, line_h: float, extra_lines: int = 0) -> int:
    """Estimación de líneas usando longitud de caracteres y ancho disponible.

    - Calcula un promedio de ancho por carácter con la fuente actual.
    - Estima cuántos caracteres caben por línea y deriva el número de líneas.
    - Puede sumar `extra_lines` si se desea holgura fija (por defecto 0).
    """
    t = _to_pdf_compatible(_norm_newlines(text or ""))
    if not t:
        return max(1, extra_lines)
    # Ancho promedio por carácter basado en una muestra de caracteres comunes
    sample = _to_pdf_compatible("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzñáéíóúÑÁÉÍÓÚ 0123456789")
    sample_w = pdf.get_string_width(sample) or 1.0
    avg_char_w = max(0.1, sample_w / max(1, len(sample)))
    chars_per_line = max(1, int(width / avg_char_w))
    total_lines = 0
    for seg in t.splitlines() or [t]:
        seg_len = len(seg)
        total_lines += max(1, math.ceil(seg_len / chars_per_line))
    return total_lines + max(0, int(extra_lines))
 


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
