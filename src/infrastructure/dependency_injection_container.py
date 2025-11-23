from adapters.data_cleaner_adapter import PandasDataCleaner
from adapters.repositories.analysis_repository_adapter import \
    SQLandCSVAnalysisRepository
from adapters.sentiment_analyzer_adapter import JoblibSentimentAnalyzer
from adapters.file_readers.file_reader_adapter import PandasFileReader
from infrastructure.config import settings
from use_cases.load_analysis_use_case import LoadAnalysisUseCase
from use_cases.list_analyses_use_case import ListAnalysesUseCase
from use_cases.process_file_use_case import ProcessFileUseCase
from use_cases.delete_analysis_use_case import DeleteAnalysisUseCase
from use_cases.read_file_use_case import ReadFileUseCase
from use_cases.prepare_analysis_display_use_case import \
    PrepareAnalysisDisplayUseCase
from infrastructure.ui.controllers.streamlit_controller import \
    StreamlitController
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
        # Crear instances de nuestros adaptadores

        # 1. Adaptador de Repositorio
        db_config = {
            'host': settings.DB_HOST,
            'user': settings.DB_USER,
            'password': settings.DB_PASSWORD,
            'database': settings.DB_NAME,
            'port': settings.DB_PORT
        }

        logger.info("Inicializando SQLandCSVAnalysisRepository con la"
                    f" configuración de BD: {db_config}")

        self._analysis_repository = SQLandCSVAnalysisRepository(
            db_config=db_config,
            csv_base_dir=settings.CSV_BASE_DIR)

        # 2. Adaptador de Analizador de Sentimiento
        # Construir la ruta al modelo de manera robusta usando __file__
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(
            current_dir, "ML", "clasificador_sentimiento_final.pkl")
        logger.info(f"Cargando modelo desde: {model_path}")
        self._sentiment_analyzer = JoblibSentimentAnalyzer(
            model_path=model_path)

        # 3. Adaptador de Limpiador de Datos
        self._data_cleaner = PandasDataCleaner()

        # 4. Adaptador de Lector de Archivos
        self._file_reader = PandasFileReader(
            required_sheets=settings.EXCEL_REQUIRED_SHEETS)

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

    @property
    def read_file_use_case(self) -> ReadFileUseCase:
        """
        Crea y devuelve una instancia de ReadFileUseCase.
        """
        return ReadFileUseCase(file_reader=self._file_reader)

    @property
    def prepare_analysis_display_use_case(
            self) -> PrepareAnalysisDisplayUseCase:
        """
        Crea y devuelve una instancia de PrepareAnalysisDisplayUseCase.
        """
        return PrepareAnalysisDisplayUseCase()

    @property
    def streamlit_controller(self) -> StreamlitController:
        """
        Crea y devuelve una instancia de StreamlitController con todas las
        dependencias inyectadas.
        """
        return StreamlitController(
            read_file_use_case=self.read_file_use_case,
            process_file_use_case=self.process_file_use_case,
            load_analysis_use_case=self.load_analysis_use_case,
            list_analyses_use_case=self.list_analyses_use_case,
            delete_analysis_use_case=self.delete_analysis_use_case,
            prepare_analysis_display_use_case=self.
            prepare_analysis_display_use_case,
        )


# Una instancia global del contenedor que la aplicación puede usar
container = Container()
