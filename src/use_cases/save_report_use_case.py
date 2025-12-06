import os
from typing import Tuple

import pandas as pd

from use_cases.ports.report_repository import IReportRepository
from infrastructure.ui.export import generate_excel_export
from infrastructure.ui.export_pdf import generate_pdf_export


class SaveReportUseCase:
    """Genera y guarda un reporte (archivo + historial)."""

    def __init__(
        self,
        report_repository: IReportRepository,
        reports_base_dir: str = "reports",
    ):
        self._report_repository = report_repository
        self._reports_base_dir = reports_base_dir
        os.makedirs(self._reports_base_dir, exist_ok=True)

    def execute(
        self,
        analysis_name: str,
        df: pd.DataFrame,
        report_format: str = "pdf",
        color_map=None,
    ) -> Tuple[bool, str, str]:
        """
        Genera el archivo y persiste su metadato.

        Returns: (success, message, file_path)
        """
        if df is None or df.empty:
            return False, "No hay datos para generar el reporte.", ""
        safe_name = analysis_name.replace(" ", "_")
        ext = ".pdf" if report_format.lower() == "pdf" else ".xlsx"
        filename = f"reporte_{safe_name}{ext}"
        file_path = os.path.join(self._reports_base_dir, filename)

        try:
            if report_format.lower() == "pdf":
                content = generate_pdf_export(df, color_map)
                with open(file_path, "wb") as f:
                    f.write(content)
            else:
                content = generate_excel_export(df)
                with open(file_path, "wb") as f:
                    f.write(content)
        except Exception as e:
            return False, f"Error al generar/guardar archivo: {e}", ""

        # Calcular metadatos del reporte (SRP aislado en método privado)
        source_file_name, date_range, comments_count = self._compute_metadata(
            analysis_name, df
        )

        ok, msg = self._report_repository.save(
            analysis_name,
            report_format.lower(),
            file_path,
            source_file_name=source_file_name,
            date_range=date_range,
            comments_count=comments_count,
        )
        if not ok:
            # Aún dejamos el archivo en disco para recuperación manual
            return False, msg, file_path
        return True, msg, file_path

    def _compute_metadata(
        self, analysis_name: str, df: pd.DataFrame
    ) -> Tuple[str, str, int]:
        source_file_name = analysis_name
        comments_count = int(len(df))
        date_range = None
        if "fecha" in df.columns:
            try:
                fechas = pd.to_datetime(df["fecha"]).dropna()
                if not fechas.empty:
                    date_range = (
                        f"{fechas.min().date()} - {fechas.max().date()}"
                    )
            except Exception:
                date_range = None
        return source_file_name, date_range, comments_count
