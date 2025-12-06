from abc import ABC, abstractmethod
from typing import List, Tuple, Dict


class INoteRepository(ABC):
    @abstractmethod
    def add(self, analysis_name: str, content: str) -> Tuple[bool, str]:
        pass

    @abstractmethod
    def get_all(self, analysis_name: str) -> List[Dict]:
        pass

    @abstractmethod
    def delete(self, note_id: int) -> Tuple[bool, str]:
        pass
