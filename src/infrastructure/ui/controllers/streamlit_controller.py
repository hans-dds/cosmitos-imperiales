import pandas as pd
from typing import Optional, Tuple, List, Dict

from use_cases.process_file_use_case import ProcessFileUseCase
from use_cases.read_file_use_case import ReadFileUseCase
from use_cases.load_analysis_use_case import LoadAnalysisUseCase
from use_cases.list_analyses_use_case import ListAnalysesUseCase
from use_cases.delete_analysis_use_case import DeleteAnalysisUseCase
from use_cases.prepare_analysis_display_use_case import PrepareAnalysisDisplayUseCase
from use_cases.send_results_email_use_case import SendResultsEmailUseCase
from use_cases.save_report_use_case import SaveReportUseCase
from use_cases.list_reports_use_case import ListReportsUseCase
from use_cases.clear_reports_history_use_case import ClearReportsHistoryUseCase
from infrastructure.ui.constants import ALL_ANALYSES_OPTION
import os


class StreamlitController:
    """
    Controlador que orquesta la interacción entre la UI de Streamlit
    y los casos de uso de la aplicación.
    """

    def __init__(
        self,
        read_file_use_case: ReadFileUseCase,
        process_file_use_case: ProcessFileUseCase,
        load_analysis_use_case: LoadAnalysisUseCase,
        list_analyses_use_case: ListAnalysesUseCase,
        delete_analysis_use_case: DeleteAnalysisUseCase,
        prepare_analysis_display_use_case: PrepareAnalysisDisplayUseCase,
        send_results_email_use_case: SendResultsEmailUseCase,
        save_report_use_case: SaveReportUseCase,
        list_reports_use_case: ListReportsUseCase,
        clear_reports_history_use_case: ClearReportsHistoryUseCase,
    ):
        self._read_file_use_case = read_file_use_case
        self._process_file_use_case = process_file_use_case
        self._load_analysis_use_case = load_analysis_use_case
        self._list_analyses_use_case = list_analyses_use_case
        self._delete_analysis_use_case = delete_analysis_use_case
        self._prepare_analysis_display_use_case = prepare_analysis_display_use_case
        self._send_results_email_use_case = send_results_email_use_case
        self._save_report_use_case = save_report_use_case
        self._list_reports_use_case = list_reports_use_case
        self._clear_reports_history_use_case = clear_reports_history_use_case

    def handle_file_upload(
        self,
        uploaded_file,
        file_basename: str
    ) -> Tuple[bool, Optional[pd.DataFrame], Optional[str]]:
        """
        Maneja la carga y procesamiento de un archivo.

        Args:
            uploaded_file: El objeto de archivo cargado desde Streamlit.
            file_basename: El nombre base del archivo (sin extensión).

        Returns:
            Tupla con (éxito, DataFrame analizado, mensaje de error)
        """
        try:
            # Leer el archivo usando el caso de uso
            raw_df = self._read_file_use_case.execute(
                uploaded_file,
                uploaded_file.type
            )

            # Procesar el archivo (limpiar, analizar y guardar)
            analyzed_df = self._process_file_use_case.execute(
                raw_df,
                file_basename
            )

            return True, analyzed_df, None

        except ValueError as e:
            return False, None, str(e)
        except Exception as e:
            return False, None, f"Error inesperado: {str(e)}"

    def handle_load_analysis(
        self,
        analysis_name: str
    ) -> Tuple[bool, Optional[pd.DataFrame], Optional[str]]:
        """
        Maneja la carga de un análisis guardado.
        Args:
            analysis_name: El nombre del análisis a cargar.
        Returns:
            Tupla con (éxito, DataFrame cargado, mensaje de error)
        """
        try:
            if analysis_name == ALL_ANALYSES_OPTION:
                return self._handle_load_all_analyses()
            loaded_df = self._load_analysis_use_case.execute(analysis_name)
            if loaded_df.empty:
                return (False, None,
                        f"No se encontraron datos para el análisis "
                        f"'{analysis_name}'.")
            return True, loaded_df, None
        except Exception as e:
            return False, None, f"Error al cargar el análisis: {str(e)}"

    def get_saved_analyses(self) -> List[str]:
        """
        Obtiene la lista de análisis guardados.
        Returns:
            Lista de nombres de análisis guardados.
        """
        return self._list_analyses_use_case.execute()

    def handle_delete_analysis(
        self,
        analysis_name: str
    ) -> Tuple[bool, str]:
        """
        Maneja la eliminación de un análisis.
        Args:
            analysis_name: El nombre del análisis a eliminar.
        Returns:
            Tupla con (éxito, mensaje)
        """
        return self._delete_analysis_use_case.execute(analysis_name)

    def handle_delete_multiple_analyses(
        self,
        analysis_names: List[str]
    ) -> Tuple[bool, List[Tuple[str, bool, str]]]:
        """
        Maneja la eliminación de múltiples análisis.
        Args:
            analysis_names: Lista de nombres de análisis a eliminar.
        Returns:
            Tupla con (éxito general, lista de resultados individuales)
        """
        return self._delete_analysis_use_case.execute_multiple(
            analysis_names)

    def prepare_analysis_display(
        self,
        df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """
        Prepara un DataFrame para visualización.
        Args:
            df: DataFrame con los datos del análisis
        Returns:
            Tupla con (DataFrame preparado, mapa de colores)
        """
        return self._prepare_analysis_display_use_case.execute(df)
    
    def handle_send_email(
        self,
        to_emails: List[str],
        analysis_name: str,
        df: pd.DataFrame,
        attachment_type: str = 'excel',
        color_map: Dict[str, str] = None,
        comments_df: pd.DataFrame | None = None,
    ) -> Tuple[bool, str]:
        """
        Maneja el envío de resultados por correo electrónico.

        Args:
            to_emails: Lista de correos destinatarios.
            analysis_name: Nombre del análisis.
            df: DataFrame con los datos del análisis.
            attachment_type: Tipo de adjunto ('excel' o 'pdf').
            color_map: Mapa de colores (necesario para PDF).

        Returns:
            Tupla con (éxito, mensaje)
        """
        return self._send_results_email_use_case.execute(
            to_emails=to_emails,
            analysis_name=analysis_name,
            df=df,
            attachment_type=attachment_type,
            color_map=color_map,
            comments_df=comments_df,
        )

    def handle_save_report(
        self,
        analysis_name: str,
        df: pd.DataFrame,
        report_format: str = 'pdf',
        color_map: Dict[str, str] = None
    ) -> Tuple[bool, str, str]:
        """Genera y guarda un reporte en historial."""
        return self._save_report_use_case.execute(analysis_name, df, report_format, color_map)

    def get_report_history(self) -> List[dict]:
        """Obtiene historial de reportes guardados."""
        return self._list_reports_use_case.execute()

    def clear_report_history(self) -> Tuple[bool, str]:
        """Limpia el historial de reportes."""
        return self._clear_reports_history_use_case.execute()

    def get_report_bytes(self, file_path: str) -> Tuple[bool, Optional[bytes]]:
        """Lee y devuelve el contenido del archivo de reporte.

        Args:
            file_path: Ruta absoluta al archivo del reporte.

        Returns:
            Tupla (ok, bytes) donde ok indica éxito y bytes el contenido.
        """
        try:
            if not file_path or not os.path.exists(file_path):
                return False, None
            with open(file_path, 'rb') as f:
                return True, f.read()
        except Exception:
            return False, None

    def _handle_load_all_analyses(self) -> Tuple[bool, Optional[pd.DataFrame], Optional[str]]:
        """
        Carga y consolida todos los análisis guardados en la base de datos.
        Returns:
            Tupla con (éxito, DataFrame consolidado, mensaje de error)
        """
        try:
            analysis_names = self._list_analyses_use_case.execute()
            if not analysis_names:
                return (False, None,
                        "No hay análisis guardados para consolidar.")
            dataframes = []
            for name in analysis_names:
                df = self._load_analysis_use_case.execute(name)
                if df.empty:
                    continue
                df = df.copy()
                df['analysis_name'] = name
                dataframes.append(df)
            if not dataframes:
                return (False, None,
                        "No se encontraron datos en los análisis guardados.")
            combined_df = pd.concat(dataframes, ignore_index=True)
            return True, combined_df, None
        except Exception as e:
            return False, None, f"Error al consolidar los análisis: {str(e)}"
