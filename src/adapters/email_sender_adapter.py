import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import logging
from typing import List, Optional
import os

logger = logging.getLogger(__name__)


class SmtpEmailSender:
    """
    Adaptador para enviar correos electrónicos usando SMTP.
    """

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str,
        email_from: str,
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.email_from = email_from

    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        attachment_path: Optional[str] = None,
    ) -> bool:
        """
        Envía un correo electrónico a una lista de destinatarios.

        Args:
            to_emails: Lista de direcciones de correo electrónico.
            subject: Asunto del correo.
            body: Cuerpo del correo (texto plano).
            attachment_path: Ruta al archivo adjunto (opcional).

        Returns:
            True si el envío fue exitoso, False en caso contrario.
        """
        if not to_emails:
            logger.warning(
                "No se proporcionaron destinatarios para el correo."
            )
            return False

        msg = MIMEMultipart()
        msg["From"] = self.email_from
        msg["To"] = ", ".join(to_emails)
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        if attachment_path:
            try:
                # Determine MIME type
                content_type = "application/octet-stream"
                if attachment_path.endswith(".xlsx"):
                    content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                elif attachment_path.endswith(".pdf"):
                    content_type = "application/pdf"

                with open(attachment_path, "rb") as f:
                    part = MIMEApplication(
                        f.read(),
                        _subtype=content_type.split("/")[-1],
                        Name=os.path.basename(attachment_path),
                    )
                    # Force the content type header to be full
                    part.replace_header(
                        "Content-Type",
                        f'{content_type}; name="{os.path.basename(attachment_path)}"',
                    )

                # After the file is closed
                part["Content-Disposition"] = (
                    f'attachment; filename="{os.path.basename(attachment_path)}"'
                )
                msg.attach(part)
            except Exception as e:
                logger.error(
                    f"Error al adjuntar archivo {attachment_path}: {e}"
                )
                return False

        try:
            # Conexión al servidor SMTP
            # Nota: Para servidores reales (Gmail, Outlook), se requeriría starttls() y login()
            # Aquí asumimos una configuración que puede variar.
            # Implementación básica compatible con servidor de depuración (localhost) y servidores con auth.

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                # server.set_debuglevel(1) # Descomentar para debug

                # Si se proporcionan credenciales, intentar login
                if self.smtp_user and self.smtp_password:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)

                server.send_message(msg)

            logger.info(f"Correo enviado exitosamente a: {to_emails}")
            return True

        except Exception as e:
            logger.error(f"Error al enviar correo: {e}")
            return False
