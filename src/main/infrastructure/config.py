import os
from dotenv import load_dotenv
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Construir la ruta al archivo .env en la raíz del proyecto
dotenv_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
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
    DB_NAME: str = os.getenv("DB_NAME", "database")
    logger.info("Configuración cargada: "
                 f"DB_HOST={DB_HOST}, DB_USER={DB_USER}, "
                 f"DB_NAME={DB_NAME}, "
                 f"DB_PASSWORD={DB_PASSWORD}")


settings = Settings()
