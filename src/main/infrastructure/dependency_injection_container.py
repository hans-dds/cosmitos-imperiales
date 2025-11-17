from adapters.data_cleaner_adapter import PandasDataCleaner
from adapters.repositories.analysis_repository_adapter import \
    SQLandCSVAnalysisRepository
from adapters.sentiment_analyzer_adapter import JoblibSentimentAnalyzer
from infrastructure.config import settings
from use_cases.load_analysis_use_case import LoadAnalysisUseCase
from use_cases.list_analyses_use_case import ListAnalysesUseCase
from use_cases.process_file_use_case import ProcessFileUseCase
from use_cases.delete_analysis_use_case import DeleteAnalysisUseCase
import logging
import os
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Container:
    """
    Un contenedor de inyección de dependencias simple para crear y conectar
    servicios.
    """

    def __init__(self):
        # Crear instancias de nuestros adaptadores

        # 1. Adaptador de Repositorio
        db_config = {
            'host': settings.DB_HOST,
            'user': settings.DB_USER,
            'password': settings.DB_PASSWORD,
            'database': settings.DB_NAME
        }

        logger.info("Inicializando SQLandCSVAnalysisRepository con la configuración de BD: "
                    f"{db_config}")

        self._analysis_repository = SQLandCSVAnalysisRepository(
            db_config=db_config)

        # 2. Adaptador de Analizador de Sentimiento
        # Construir la ruta al modelo de manera robusta usando __file__
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, "ML", "clasificador_sentimiento_final.pkl")
        logger.info(f"Cargando modelo desde: {model_path}")
        self._sentiment_analyzer = JoblibSentimentAnalyzer(
            model_path=model_path)

        # 3. Adaptador de Limpiador de Datos
        self._data_cleaner = PandasDataCleaner()

    @property
    def process_file_use_case(self) -> ProcessFileUseCase:
        """
        Crea y devuelve una instancia de ProcessFileUseCase con todas las
        dependencias inyectadas.
        """
        return ProcessFileUseCase(
            data_cleaner=self._data_cleaner,
            sentiment_analyzer=self._sentiment_analyzer,
            analysis_repository=self._analysis_repository,
        )

    @property
    def list_analyses_use_case(self) -> ListAnalysesUseCase:
        """
        Crea y devuelve una instancia de ListAnalysesUseCase.
        """
        return ListAnalysesUseCase(
            analysis_repository=self._analysis_repository)

    @property
    def load_analysis_use_case(self) -> LoadAnalysisUseCase:
        """
        Crea y devuelve una instancia de LoadAnalysisUseCase.
        """
        return LoadAnalysisUseCase(
            analysis_repository=self._analysis_repository)

    @property
    def delete_analysis_use_case(self) -> DeleteAnalysisUseCase:
        """
        Crea y devuelve una instancia de DeleteAnalysisUseCase.
        """
        return DeleteAnalysisUseCase(
            analysis_repository=self._analysis_repository)


# Una instancia global del contenedor que la aplicación puede usar
container = Container()
