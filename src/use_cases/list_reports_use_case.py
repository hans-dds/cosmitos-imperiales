from typing import List

from use_cases.ports.report_repository import IReportRepository


class ListReportsUseCase:
    """Lista historial de reportes generados."""

    def __init__(self, report_repository: IReportRepository):
        self._report_repository = report_repository

    def execute(self) -> List[dict]:
        return self._report_repository.list()
