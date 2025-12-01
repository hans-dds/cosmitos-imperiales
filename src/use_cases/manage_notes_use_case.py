from typing import List, Dict
from use_cases.ports.note_repository import INoteRepository

class ManageNotesUseCase:
    def __init__(self, note_repository: INoteRepository):
        self._repository = note_repository

    def add_note(self, analysis_name: str, content: str) -> bool:
        if not content or not content.strip():
            return False
        return self._repository.add_note(analysis_name, content)

    def get_notes(self, analysis_name: str) -> List[Dict]:
        return self._repository.get_notes(analysis_name)

    def delete_note(self, note_id: int) -> bool:
        return self._repository.delete_note(note_id)
        
    def update_note(self, note_id: int, content: str) -> bool:
        return self._repository.update_note(note_id, content)