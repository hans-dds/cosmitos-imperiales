from typing import List, Tuple, Dict
import logging
import os
from adapters.email_sender_adapter import SmtpEmailSender
from infrastructure.ui.export import generate_excel_export
from infrastructure.ui.export_pdf import generate_pdf_export
import pandas as pd

import re

logger = logging.getLogger(__name__)


class SendResultsEmailUseCase:
    """
    Caso de uso para enviar los resultados del análisis por correo electrónico.
    """

    def __init__(self, email_sender: SmtpEmailSender):
        self._email_sender = email_sender
        self._email_regex = re.compile(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        )

    def execute(
        self,
        to_emails: List[str],
        analysis_name: str,
        df: pd.DataFrame,
        attachment_type: str = "excel",
        color_map: Dict[str, str] = None,
        comments_df: pd.DataFrame | None = None,
    ) -> Tuple[bool, str]:
        """
        Ejecuta el envío del correo con el reporte adjunto.

        Args:
            to_emails: Lista de correos destinatarios.
            analysis_name: Nombre del análisis.
            df: DataFrame con los datos del análisis.
            attachment_type: Tipo de adjunto ('excel' o 'pdf').
            color_map: Mapa de colores (necesario para PDF).
            comments_df: Subconjunto filtrado/ordenado de comentarios (usado para PDF y Excel para reflejar filtros de UI). Si es None, se usan todos.

        Returns:
            Tupla (exito, mensaje).
        """
        if not to_emails:
            return False, "La lista de correos está vacía."

        invalid_emails = [
            email for email in to_emails if not self._email_regex.match(email)
        ]
        if invalid_emails:
            return (
                False,
                f"Los siguientes correos no son válidos: {', '.join(invalid_emails)}",
            )

        subject = f"Reporte de Análisis: {analysis_name}"
        body = f"""Hola,

Adjunto encontrarás el reporte del análisis: {analysis_name}.

Saludos,
El equipo de Cosmitos Imperiales
"""

        temp_path = ""
        try:
            if attachment_type == "pdf":
                if color_map is None:
                    return (
                        False,
                        "Se requiere el mapa de colores para generar el PDF.",
                    )

                filename = f"reporte_{analysis_name.replace(' ', '_')}.pdf"
                temp_path = f"/tmp/{filename}"
                pdf_bytes = generate_pdf_export(
                    df, color_map, comments_df=comments_df
                )
                with open(temp_path, "wb") as f:
                    f.write(pdf_bytes)
            else:  # Excel siempre exporta todos los datos (sin filtros de comentarios)
                filename = f"reporte_{analysis_name.replace(' ', '_')}.xlsx"
                temp_path = f"/tmp/{filename}"
                excel_data = generate_excel_export(df)
                with open(temp_path, "wb") as f:
                    f.write(excel_data)

            success = self._email_sender.send_email(
                to_emails=to_emails,
                subject=subject,
                body=body,
                attachment_path=temp_path,
            )

            if success:
                return (
                    True,
                    f"Correo enviado exitosamente a {len(to_emails)} destinatarios.",
                )
            else:
                return (
                    False,
                    "Error al enviar el correo. Revisa los logs para más detalles.",
                )

        except Exception as e:
            logger.error(f"Error en SendResultsEmailUseCase: {e}")
            return False, f"Ocurrió un error inesperado: {str(e)}"
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception as e:
                    logger.warning(
                        f"No se pudo eliminar el archivo temporal {temp_path}: {e}"
                    )
