import os
from typing import List
from dotenv import load_dotenv
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Construir la ruta al archivo .env en la raíz del proyecto
dotenv_path = os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env')
load_dotenv(dotenv_path=dotenv_path)


class Settings:
    """
    Clase para gestionar la configuración de la aplicación
    con variables de entorno.
    """
    logger.info(f"Cargando configuración desde {dotenv_path}")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_USER: str = os.getenv("DB_USER", "user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")
    DB_NAME: str = os.getenv("DB_NAME", "cosmitos_imperiales_db")
    
    # Configuración de archivos Excel
    EXCEL_REQUIRED_SHEETS: List[str] = os.getenv(
        "EXCEL_REQUIRED_SHEETS", "ATC,Encuesta salida"
    ).split(",")
    
    # Configuración de directorio CSV
    CSV_BASE_DIR: str = os.getenv("CSV_BASE_DIR", "datos_analizados")
    
    # Configuración de UI
    APP_TITLE: str = os.getenv("APP_TITLE", "Gestor de Satisfacción y Seguimiento de Posventa")

    LLM_API_KEY="tu_api_key_secreta_aqui"
    LLM_API_URL="httpsE://api.openai.com/v1/chat/completions"
    
    logger.info("Configuración cargada: "
                f"DB_HOST={DB_HOST}, DB_USER={DB_USER},"
                f"DB_NAME={DB_NAME}, "
                f"DB_PASSWORD={DB_PASSWORD}, "
                f"EXCEL_REQUIRED_SHEETS={EXCEL_REQUIRED_SHEETS}, "
                f"CSV_BASE_DIR={CSV_BASE_DIR}")


settings = Settings()
