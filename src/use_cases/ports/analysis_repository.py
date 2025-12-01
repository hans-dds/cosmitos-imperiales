from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Tuple


from abc import ABC, abstractmethod
from typing import List, Tuple
import pandas as pd


class IAnalysisRepository(ABC):
    """Puerto simplificado para la persistencia de análisis.

    Agnóstico del medio de almacenamiento: la implementación puede guardar
    en múltiples destinos (SQL, CSV, etc.) sin exponer métodos específicos.
    """

    @abstractmethod
    def save(self, data: pd.DataFrame, analysis_id: str) -> Tuple[bool, str]:
        """Persiste un análisis identificado por `analysis_id`."""
        raise NotImplementedError

    @abstractmethod
    def list(self) -> List[str]:
        """Lista identificadores de análisis disponibles."""
        raise NotImplementedError

    @abstractmethod
    def load(self, analysis_id: str) -> pd.DataFrame:
        """Recupera un análisis por su identificador."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, analysis_id: str) -> Tuple[bool, str]:
        """Elimina un análisis por su identificador."""
        raise NotImplementedError

    @abstractmethod
    def delete_many(self, analysis_ids: List[str]) -> Tuple[bool, List[Tuple[str, bool, str]]]:
        """Elimina múltiples análisis y retorna resultados individuales."""
        raise NotImplementedError

    @abstractmethod
    def clone_with_modifications(
        self, 
        original_analysis_id: str, 
        modified_data: pd.DataFrame, 
        suffix: str
    ) -> Tuple[bool, str, str]:
        """
        Clona un análisis existente con datos modificados.
        
        Args:
            original_analysis_id: ID del análisis original
            modified_data: DataFrame con los datos modificados
            suffix: Sufijo para el nuevo análisis (ej: '_modificacion_2024-12-01')
        
        Returns:
            Tupla con (éxito, nuevo_analysis_id, mensaje)
        """
        raise NotImplementedError
