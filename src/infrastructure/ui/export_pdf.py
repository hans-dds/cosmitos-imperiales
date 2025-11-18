"""
Módulo de exportación a PDF.

Este módulo se encarga de generar reportes PDF con tablas, gráficos y
comentarios, delegando el cálculo de métricas a los servicios del dominio.
"""

from datetime import datetime
from io import BytesIO
from textwrap import wrap
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

# Ajustes generales del reporte
_MAX_COMMENTS = 15
_CHART_WIDTH = 180  # mm


class _ReportePDF(FPDF):
    """FPDF con cabecera y pie consistente."""

    def __init__(self, titulo: str) -> None:
        super().__init__(orientation="P", unit="mm", format="A4")
        self.titulo = titulo

    def header(self) -> None:  # pragma: no cover - comportamiento nativo de FPDF  # noqa
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, self.titulo, new_x="LMARGIN", new_y="NEXT",
                  align="C")
        self.ln(2)

    def footer(self) -> None:  # pragma: no cover - comportamiento nativo de FPDF # noqa
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")


def generate_pdf_export(
        df: pd.DataFrame,
        color_map: Dict[str, str] = None) -> bytes:
    """
    Genera un PDF con tablas, comentarios y gráficas.

    Args:
        df: DataFrame con las columnas esperadas (Clasificacion, comentarios,
        calificacion, longitud).
        color_map: Mapa de colores utilizado en la vista principal. Si es
        None, usa el del dominio.

    Returns:
        Bytes del archivo PDF listo para descargar.
    """
    # Validar que el DataFrame no esté vacío
    if df is None or df.empty:
        raise ValueError(
            "El DataFrame está vacío. No se puede generar el PDF.")
    # Usar mapa de colores del dominio si no se proporciona
    if color_map is None:
        color_map = get_color_map()
    try:
        # Preparar datos usando servicios del dominio
        datos = _preparar_dataframe(df)
        # Validar que hay datos después de la preparación
        if datos.empty:
            raise ValueError("No hay datos válidos para generar el PDF.")
        # Crear PDF
        pdf = _ReportePDF("Reporte de comentarios")
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        # Renderizar secciones
        _render_resumen(pdf, datos)
        # Crear y renderizar gráficos
        figuras = _crear_figuras(datos, color_map)
        if figuras:
            _render_charts(pdf, figuras)
        else:
            pdf.set_font("Helvetica", "I", 10)
            pdf.cell(0, 8, "No se pudieron generar las visualizaciones.",
                     new_x="LMARGIN", new_y="NEXT")
            pdf.ln(4)
        # Renderizar comentarios
        _render_comments(pdf, datos)
        # Generar contenido
        contenido = pdf.output(dest="S")
        # Validar que el contenido no esté vacío
        if not contenido or (
                isinstance(
                    contenido,
                    (str,
                     bytes,
                     bytearray)) and len(contenido) == 0):
            raise ValueError("El PDF generado está vacío.")
        # fpdf2 puede regresar str o bytearray, convertimos explícitamente a
        # bytes para Streamlit.
        if isinstance(contenido, str):
            return contenido.encode("latin-1")
        if isinstance(contenido, bytearray):
            return bytes(contenido)
        return contenido
    except Exception as e:
        # Si hay un error, crear un PDF con el mensaje de error
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
    """
    Prepara el DataFrame para la generación del PDF.
    Args:
        df: DataFrame original
    Returns:
        DataFrame preparado con todas las columnas necesarias
    """
    datos = df.copy()
    # Asegurar columnas requeridas
    if "Clasificacion" not in datos.columns:
        datos["Clasificacion"] = "Sin Clasificación"
    datos["Clasificacion"] = datos["Clasificacion"].fillna("Sin Clasificación")
    if "comentarios" not in datos.columns:
        datos["comentarios"] = ""
    datos["comentarios"] = datos["comentarios"].fillna("")
    # Calcular longitud usando servicio del dominio (longitud de caracteres)
    datos = calculate_comment_length(datos)
    # Para el PDF, también calculamos número de palabras para el histograma
    # que muestra "Número de palabras" en lugar de caracteres
    if "num_palabras" not in datos.columns:
        datos["num_palabras"] = datos["comentarios"].astype(
            str).str.split().str.len()
    if "calificacion" not in datos.columns:
        datos["calificacion"] = "-"
    return datos


def _render_resumen(pdf: _ReportePDF, datos: pd.DataFrame) -> None:
    """
    Renderiza la sección de resumen en el PDF.
    Args:
        pdf: Instancia del PDF
        datos: DataFrame con los datos
    """
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
    # Usar servicio del dominio para calcular resumen
    resumen = calculate_summary_metrics(datos)
    # Validar que el resumen no esté vacío
    if resumen.empty:
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 8, "No hay datos suficientes para generar el resumen.",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)
        return
    # Si el resumen tiene Porcentaje, no lo usamos en la tabla del PDF
    # Solo mostramos Clasificación, cantidad y longitud promedio
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Resumen por categoría", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(213, 245, 73)
    pdf.cell(60, 8, "Clasificación", border=1, fill=True)
    pdf.cell(40, 8, "Comentarios", border=1, fill=True, align="C")
    pdf.cell(50, 8, "Longitud promedio", border=1, fill=True, align="C")
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 10)
    for _, fila in resumen.iterrows():
        clasificacion = str(fila.get("Clasificacion", "Sin clasificación"))
        num_comentarios = int(fila.get("NumComentarios", 0))
        longitud_prom = float(fila.get("LongitudPromedio", 0))
        pdf.cell(60, 8, clasificacion, border=1)
        pdf.cell(40, 8, str(num_comentarios), border=1, align="C")
        pdf.cell(50, 8, f"{longitud_prom:.1f}", border=1, align="C")
        pdf.ln(8)
    pdf.ln(4)


def _crear_figuras(
    datos: pd.DataFrame,
    color_map: Dict[str, str]
) -> List[Tuple[str, 'plotly.graph_objs.Figure']]:
    """
    Crea las figuras de Plotly para incluir en el PDF.
    Args:
        datos: DataFrame con los datos
        color_map: Mapa de colores
    Returns:
        Lista de tuplas (título, figura)
    """
    # Validar que hay datos
    if datos.empty or "Clasificacion" not in datos.columns:
        return []
    # Normalizar mapa de colores para diferentes variaciones de texto
    clasificaciones_unicas = datos["Clasificacion"].dropna().unique()
    if len(clasificaciones_unicas) == 0:
        return []
    mapa_colores = _normalizar_color_map(color_map, clasificaciones_unicas)
    # Conteo por clasificación
    conteo = datos["Clasificacion"].value_counts().reset_index()
    conteo.columns = ["Clasificacion", "cantidad"]
    # Validar que hay datos para los gráficos
    if conteo.empty:
        return []
    # Gráfico de pastel
    fig_pie = px.pie(
        conteo,
        names="Clasificacion",
        values="cantidad",
        color="Clasificacion",
        color_discrete_map=mapa_colores,
        hole=0.4,
        title="Distribución de comentarios",
    )
    # Gráfico de barras
    fig_bar = px.bar(
        conteo,
        x="Clasificacion",
        y="cantidad",
        color="Clasificacion",
        text="cantidad",
        color_discrete_map=mapa_colores,
        title="Comentarios por categoría",
    )
    # Histograma de longitud (usar número de palabras para el PDF)
    # Si no existe num_palabras, usar longitud de caracteres
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
    """
    Renderiza las gráficas en el PDF.
    Args:
        pdf: Instancia del PDF
        figuras: Lista de tuplas (título, figura)
    """
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
            # Si falla la conversión de la imagen, continuar con la siguiente
            pdf.set_font("Helvetica", "I", 10)
            pdf.cell(
                0,
                6,
                f"{titulo} (no disponible)",
                new_x="LMARGIN",
                new_y="NEXT")
            pdf.ln(4)


def _render_comments(pdf: _ReportePDF, datos: pd.DataFrame) -> None:
    """
    Renderiza los comentarios en el PDF.
    Args:
        pdf: Instancia del PDF
        datos: DataFrame con los datos
    """
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Comentarios recientes", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    # Validar que hay datos
    if datos.empty:
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 8, "No hay comentarios para mostrar.",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)
        return
    seleccion = datos.head(_MAX_COMMENTS)
    if seleccion.empty:
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 8, "No hay comentarios para mostrar.",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)
        return
    pdf.set_font("Helvetica", "", 10)
    for _, fila in seleccion.iterrows():
        # Obtener valores con fallbacks
        clasificacion = str(fila.get('Clasificacion', 'Sin clasificación'))
        calificacion = str(fila.get('calificacion', '-'))
        comentario = str(fila.get('comentarios', '(Sin comentario)')).strip()
        encabezado = f"{clasificacion} | Calificación: {calificacion}"
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 6, encabezado, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        texto = comentario or "(Sin comentario)"
        for linea in wrap(texto, 110):
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(0, 5, linea, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)


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
