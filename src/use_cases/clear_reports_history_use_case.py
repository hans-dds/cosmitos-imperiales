from typing import Tuple

from use_cases.ports.report_repository import IReportRepository


class ClearReportsHistoryUseCase:
    """Caso de uso para limpiar el historial de reportes."""

    def __init__(self, report_repository: IReportRepository):
        self._report_repository = report_repository

    def execute(self) -> Tuple[bool, str]:
        return self._report_repository.clear()
