from typing import List, Optional, Tuple


class IReportRepository:
    """Puerto para persistencia y consulta de historial de reportes."""

    def save(self, analysis_name: str, report_format: str, file_path: str) -> Tuple[bool, str]:
        """Guarda metadatos del reporte generado."""
        raise NotImplementedError()

    def list(self) -> List[dict]:
        """Lista historial de reportes con sus metadatos."""
        raise NotImplementedError()

    def get(self, report_id: int) -> Optional[dict]:
        """Obtiene metadatos de un reporte por id."""
        raise NotImplementedError()

    def clear(self) -> Tuple[bool, str]:
        """Limpia el historial de reportes y (opcionalmente) archivos asociados."""
        raise NotImplementedError()

    def delete(self, report_id: int) -> Tuple[bool, str]:
        """Elimina un reporte por id y borra su archivo del disco si existe."""
        raise NotImplementedError()
