"""Generación de reportes PDF con las mismas visualizaciones de la vista principal."""
from __future__ import annotations

from datetime import datetime
from io import BytesIO
from textwrap import wrap
from typing import Dict, Iterable, List, Tuple

import pandas as pd
import plotly.express as px
import plotly.io as pio
from fpdf import FPDF

# Ajustes generales del reporte
_MAX_COMMENTS = 15
_CHART_WIDTH = 180  # mm


class _ReportePDF(FPDF):
    """FPDF con cabecera y pie consistente."""

    def __init__(self, titulo: str) -> None:
        super().__init__(orientation="P", unit="mm", format="A4")
        self.titulo = titulo

    def header(self) -> None:  # pragma: no cover - comportamiento nativo de FPDF
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, self.titulo, new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(2)

    def footer(self) -> None:  # pragma: no cover - comportamiento nativo de FPDF
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")


def generar_pdf(df: pd.DataFrame, color_discrete_map: Dict[str, str]) -> bytes:
    """Genera un PDF con tablas, comentarios y gráficas.

    Args:
        df: DataFrame con las columnas esperadas (Clasificacion, comentarios, calificacion, longitud).
        color_discrete_map: Mapa de colores utilizado en la vista principal.
    Returns:
        Bytes del archivo PDF listo para descargar.
    """
    datos = _preparar_dataframe(df)
    pdf = _ReportePDF("Reporte de comentarios")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    _render_resumen(pdf, datos)
    figuras = _crear_figuras(datos, color_discrete_map)
    _render_charts(pdf, figuras)
    _render_comments(pdf, datos)

    contenido = pdf.output(dest="S")
    # fpdf2 puede regresar str o bytearray, convertimos explícitamente a bytes para Streamlit.
    if isinstance(contenido, str):
        return contenido.encode("latin-1")
    if isinstance(contenido, bytearray):
        return bytes(contenido)
    return contenido


def _preparar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    datos = df.copy()
    if "Clasificacion" not in datos.columns:
        datos["Clasificacion"] = "Sin Clasificación"
    datos["Clasificacion"] = datos["Clasificacion"].fillna("Sin Clasificación")

    if "comentarios" not in datos.columns:
        datos["comentarios"] = ""
    datos["comentarios"] = datos["comentarios"].fillna("")

    if "longitud" not in datos.columns:
        datos["longitud"] = datos["comentarios"].astype(str).str.split().str.len()

    if "calificacion" not in datos.columns:
        datos["calificacion"] = "-"

    return datos


def _render_resumen(pdf: _ReportePDF, datos: pd.DataFrame) -> None:
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"Total de comentarios analizados: {len(datos)}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Fecha del reporte: {datetime.now().strftime('%d/%m/%Y %H:%M')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    resumen = (
        datos.groupby("Clasificacion")
        .agg(cantidad=("comentarios", "count"), longitud_promedio=("longitud", "mean"))
        .reset_index()
        .sort_values("cantidad", ascending=False)
    )

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
        pdf.cell(60, 8, str(fila["Clasificacion"]), border=1)
        pdf.cell(40, 8, str(int(fila["cantidad"])), border=1, align="C")
        pdf.cell(50, 8, f"{fila['longitud_promedio']:.1f}", border=1, align="C")
        pdf.ln(8)

    pdf.ln(4)


def _crear_figuras(datos: pd.DataFrame, color_discrete_map: Dict[str, str]) -> List[Tuple[str, 'plotly.graph_objs._figure.Figure']]:
    mapa_colores = _normalizar_color_map(color_discrete_map, datos["Clasificacion"].unique())
    conteo = datos["Clasificacion"].value_counts().reset_index()
    conteo.columns = ["Clasificacion", "cantidad"]

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

    fig_hist = px.histogram(
        datos,
        x="longitud",
        color="Clasificacion",
        nbins=15,
        barmode="overlay",
        opacity=0.8,
        labels={"longitud": "Número de palabras"},
        color_discrete_map=mapa_colores,
        title="¿Quiénes opinan más?",
    )

    return [
        ("Distribución de comentarios", fig_pie),
        ("Comentarios por categoría", fig_bar),
        ("¿Quiénes opinan más?", fig_hist),
    ]


def _render_charts(pdf: _ReportePDF, figuras: Iterable[Tuple[str, 'plotly.graph_objs._figure.Figure']]) -> None:
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Visualizaciones", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    for titulo, figura in figuras:
        imagen = BytesIO(pio.to_image(figura, format="png", scale=2, engine="kaleido"))
        imagen.seek(0)
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 6, titulo, new_x="LMARGIN", new_y="NEXT")
        pdf.image(imagen, w=_CHART_WIDTH)
        pdf.ln(4)


def _render_comments(pdf: _ReportePDF, datos: pd.DataFrame) -> None:
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Comentarios recientes", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    seleccion = datos.head(_MAX_COMMENTS)
    pdf.set_font("Helvetica", "", 10)
    for _, fila in seleccion.iterrows():
        encabezado = f"{fila['Clasificacion']} | Calificación: {fila['calificacion']}"
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 6, encabezado, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        texto = str(fila["comentarios"]).strip() or "(Sin comentario)"
        for linea in wrap(texto, 110):
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(0, 5, linea, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)


def _normalizar_color_map(color_discrete_map: Dict[str, str], categorias: Iterable[str]) -> Dict[str, str]:
    mapa = {}
    for clave, valor in color_discrete_map.items():
        mapa[clave] = valor
        mapa[clave.lower()] = valor
        mapa[clave.upper()] = valor
        mapa[clave.capitalize()] = valor

    for categoria in categorias:
        if categoria not in mapa:
            clave = str(categoria).lower()
            if clave in color_discrete_map:
                mapa[categoria] = color_discrete_map[clave]

    return mapa
