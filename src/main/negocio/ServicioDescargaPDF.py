import streamlit as st
import pdfkit
import os
import base64
import tempfile
import streamlit.components.v1 as components

def boton_imprimir_pdf():
    """
    Agrega un botón HTML que abre el cuadro de diálogo de impresión del navegador.
    El usuario puede seleccionar "Guardar como PDF".
    """
    show_print_button = """
    <script>
        function print_page(obj) {
            obj.style.display = "none";
            parent.window.print();
        }
    </script>
    <button onclick="print_page(this)" style="
        background-color:#008CBA;
        color:white;
        border:none;
        padding:10px 16px;
        text-align:center;
        text-decoration:none;
        display:inline-block;
        font-size:14px;
        margin:8px 2px;
        border-radius:8px;
        cursor:pointer;
    ">
        🖨️ Imprimir / Guardar como PDF
    </button>
    """
    components.html(show_print_button)

def boton_descargar_pdf(contenido_html, nombre_archivo="informe.pdf"):
    """
    Genera un PDF a partir de HTML y muestra un botón de descarga en Streamlit.
    - contenido_html: cadena HTML que quieres convertir.
    - nombre_archivo: nombre del PDF descargable.
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
            pdfkit.from_string(contenido_html, tmpfile.name)
            tmpfile_path = tmpfile.name

        with open(tmpfile_path, "rb") as pdf_file:
            st.download_button(
                label="📄 Descargar PDF",
                data=pdf_file,
                file_name=nombre_archivo,
                mime="application/pdf"
            )
        os.remove(tmpfile_path)
    except Exception as e:
        st.error(f"Error al generar el PDF: {e}")
