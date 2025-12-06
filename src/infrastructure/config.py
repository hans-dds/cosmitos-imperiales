import os
from typing import List
from dotenv import load_dotenv
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Cargar .env desde la raíz del proyecto (ruta simplificada)
project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
dotenv_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path=dotenv_path)


class Settings:
    """
    Clase para gestionar la configuración de la aplicación
    con variables de entorno.
    """

    logger.info(f"Cargando configuración desde {dotenv_path}")
    # Prefer variables provided by docker-compose, fallback to sensible defaults
    DB_HOST: str = os.getenv("DB_HOST", os.getenv("MYSQL_HOST", "localhost"))
    DB_USER: str = os.getenv("DB_USER", os.getenv("MYSQL_USER", "user"))
    DB_PASSWORD: str = os.getenv(
        "DB_PASSWORD", os.getenv("MYSQL_PASSWORD", "password")
    )
    # docker-compose uses DB_DATABASE; also accept DB_NAME
    DB_NAME: str = os.getenv(
        "DB_NAME",
        os.getenv(
            "DB_DATABASE",
            os.getenv("MYSQL_DATABASE", "cosmitos_imperiales_db"),
        ),
    )
    # Optional DB port for local-to-container connection (e.g., 3307)
    DB_PORT: int = int(os.getenv("DB_PORT", os.getenv("MYSQL_PORT", "3306")))

    # Configuración de archivos Excel
    EXCEL_REQUIRED_SHEETS: List[str] = os.getenv(
        "EXCEL_REQUIRED_SHEETS", "ATC,Encuesta salida"
    ).split(",")

    # Configuración de directorio CSV
    CSV_BASE_DIR: str = os.getenv("CSV_BASE_DIR", "datos_analizados")

    # Configuración de UI
    APP_TITLE: str = os.getenv(
        "APP_TITLE", "Gestor de Satisfacción y Seguimiento de Posventa"
    )

    # Configuración de Email (SMTP)
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "localhost")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "1025"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@cosmitos.com")
    logger.info(
        "Configuración cargada: "
        f"DB_HOST={DB_HOST}, DB_PORT={DB_PORT}, DB_USER={DB_USER}, DB_NAME={DB_NAME}, "
        f"EXCEL_REQUIRED_SHEETS={EXCEL_REQUIRED_SHEETS}, "
        f"CSV_BASE_DIR={CSV_BASE_DIR}"
    )


settings = Settings()
