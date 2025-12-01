from adapters.data_cleaner_adapter import PandasDataCleaner
from adapters.repositories.analysis_repository_adapter import \
    SQLandCSVAnalysisRepository
from adapters.sentiment_analyzer_adapter import JoblibSentimentAnalyzer
from adapters.file_readers.file_reader_adapter import PandasFileReader
from adapters.email_sender_adapter import SmtpEmailSender
from infrastructure.config import settings
from use_cases.load_analysis_use_case import LoadAnalysisUseCase
from use_cases.list_analyses_use_case import ListAnalysesUseCase
from use_cases.process_file_use_case import ProcessFileUseCase
from use_cases.delete_analysis_use_case import DeleteAnalysisUseCase
from use_cases.read_file_use_case import ReadFileUseCase
from use_cases.prepare_analysis_display_use_case import PrepareAnalysisDisplayUseCase
from use_cases.send_results_email_use_case import SendResultsEmailUseCase
from use_cases.save_report_use_case import SaveReportUseCase
from use_cases.list_reports_use_case import ListReportsUseCase
from use_cases.clear_reports_history_use_case import ClearReportsHistoryUseCase
from use_cases.delete_report_use_case import DeleteReportUseCase
from use_cases.update_sentiment_use_case import UpdateSentimentUseCase
from adapters.repositories.report_repository_adapter import SQLReportRepository
from infrastructure.ui.controllers.streamlit_controller import StreamlitController
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
            'port': settings.DB_PORT,
            'user': settings.DB_USER,
            'password': settings.DB_PASSWORD,
            'database': settings.DB_NAME
        }

        logger.info("Inicializando SQLandCSVAnalysisRepository con la"
                f" configuración de BD: {db_config}")

        self._analysis_repository = SQLandCSVAnalysisRepository(
            db_config=db_config,
            csv_base_dir=settings.CSV_BASE_DIR)

        # Repositorio de reportes
        self._report_repository = SQLReportRepository(
            db_config=db_config,
            reports_base_dir=os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'reports')
        )

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

        # 5. Adaptador de Envío de Correos
        self._email_sender = SmtpEmailSender(
            smtp_server=settings.SMTP_SERVER,
            smtp_port=settings.SMTP_PORT,
            smtp_user=settings.SMTP_USER,
            smtp_password=settings.SMTP_PASSWORD,
            email_from=settings.EMAIL_FROM
        )

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
    def send_results_email_use_case(self) -> SendResultsEmailUseCase:
        """
        Crea y devuelve una instancia de SendResultsEmailUseCase.
        """
        return SendResultsEmailUseCase(email_sender=self._email_sender)

    @property
    def save_report_use_case(self) -> SaveReportUseCase:
        return SaveReportUseCase(report_repository=self._report_repository)

    @property
    def list_reports_use_case(self) -> ListReportsUseCase:
        return ListReportsUseCase(report_repository=self._report_repository)

    @property
    def clear_reports_history_use_case(self) -> ClearReportsHistoryUseCase:
        return ClearReportsHistoryUseCase(report_repository=self._report_repository)

    @property
    def delete_report_use_case(self) -> DeleteReportUseCase:
        return DeleteReportUseCase(report_repository=self._report_repository)

    @property
    def update_sentiment_use_case(self) -> UpdateSentimentUseCase:
        """
        Crea y devuelve una instancia de UpdateSentimentUseCase.
        """
        return UpdateSentimentUseCase(
            analysis_repository=self._analysis_repository)

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
            prepare_analysis_display_use_case=self.prepare_analysis_display_use_case,
            send_results_email_use_case=self.send_results_email_use_case,
            save_report_use_case=self.save_report_use_case,
            list_reports_use_case=self.list_reports_use_case,
            clear_reports_history_use_case=self.clear_reports_history_use_case,
            delete_report_use_case=self.delete_report_use_case,
            update_sentiment_use_case=self.update_sentiment_use_case,
        )


# Una instancia global del contenedor que la aplicación puede usar
container = Container()
