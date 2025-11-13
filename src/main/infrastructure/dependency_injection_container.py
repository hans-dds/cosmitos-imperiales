from adapters.data_cleaner_adapter import PandasDataCleaner
from adapters.repositories.analysis_repository_adapter import \
    SQLandCSVAnalysisRepository
from adapters.sentiment_analyzer_adapter import JoblibSentimentAnalyzer
from infrastructure.config import settings
from use_cases.load_analysis_use_case import LoadAnalysisUseCase
from use_cases.list_analyses_use_case import ListAnalysesUseCase
from use_cases.process_file_use_case import ProcessFileUseCase
import logging
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Container:
    """
    A simple dependency injection container for creating and wiring up
    services.
    """

    def __init__(self):
        # Create instances of our adapters

        # 1. Repository Adapter
        db_config = {
            'host': settings.DB_HOST,
            'user': settings.DB_USER,
            'password': settings.DB_PASSWORD,
            'database': settings.DB_NAME
        }

        logger.info("Initializing SQLandCSVAnalysisRepository with DB config: "
                    f"{db_config}")

        self._analysis_repository = SQLandCSVAnalysisRepository(
            db_config=db_config)

        # 2. Sentiment Analyzer Adapter
        # The path to the model should also be in the settings/config.
        # For now, I'll hardcode the path as it was in the original structure.
        model_path = "src/main/clasificador_sentimiento_final.pkl"
        self._sentiment_analyzer = JoblibSentimentAnalyzer(
            model_path=model_path)

        # 3. Data Cleaner Adapter
        self._data_cleaner = PandasDataCleaner()

    @property
    def process_file_use_case(self) -> ProcessFileUseCase:
        """
        Creates and returns an instance of the ProcessFileUseCase with all
        dependencies injected.
        """
        return ProcessFileUseCase(
            data_cleaner=self._data_cleaner,
            sentiment_analyzer=self._sentiment_analyzer,
            analysis_repository=self._analysis_repository,
        )

    @property
    def list_analyses_use_case(self) -> ListAnalysesUseCase:
        """
        Creates and returns an instance of the ListAnalysesUseCase.
        """
        return ListAnalysesUseCase(
            analysis_repository=self._analysis_repository)

    @property
    def load_analysis_use_case(self) -> LoadAnalysisUseCase:
        """
        Creates and returns an instance of the LoadAnalysisUseCase.
        """
        return LoadAnalysisUseCase(
            analysis_repository=self._analysis_repository)


# A global instance of the container that the app can use
container = Container()
