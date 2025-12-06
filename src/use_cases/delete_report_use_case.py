from typing import Tuple
from use_cases.ports.report_repository import IReportRepository


class DeleteReportUseCase:
    """Caso de uso para eliminar un reporte del historial por id."""

    def __init__(self, report_repository: IReportRepository):
        self._report_repository = report_repository

    def execute(self, report_id: int) -> Tuple[bool, str]:
        if not isinstance(report_id, int) or report_id <= 0:
            return False, "Id de reporte inválido"
        return self._report_repository.delete(report_id)
