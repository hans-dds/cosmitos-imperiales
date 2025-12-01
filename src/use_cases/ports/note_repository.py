from abc import ABC, abstractmethod
from typing import List, Tuple, Dict

class INoteRepository(ABC):
    @abstractmethod
    def add_note(self, analysis_name: str, content: str) -> bool:
        pass

    @abstractmethod
    def get_notes(self, analysis_name: str) -> List[Dict]:
        """Retorna lista de diccionarios: {'id': int, 'contenido': str, 'fecha': str}"""
        pass

    @abstractmethod
    def delete_note(self, note_id: int) -> bool:
        pass
        
    @abstractmethod
    def update_note(self, note_id: int, new_content: str) -> bool:
        pass