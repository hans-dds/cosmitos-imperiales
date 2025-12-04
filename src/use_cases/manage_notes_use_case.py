from typing import List, Dict, Tuple
from use_cases.ports.note_repository import INoteRepository

class ManageNotesUseCase:
    def __init__(self, repo: INoteRepository):
        self._repo = repo

    def add_note(self, analysis_name: str, content: str) -> Tuple[bool, str]:
        if not content.strip():
            return False, "La nota no puede estar vacía."
        return self._repo.add(analysis_name, content)

    def get_notes(self, analysis_name: str) -> List[Dict]:
        return self._repo.get_all(analysis_name)

    def delete_note(self, note_id: int) -> Tuple[bool, str]:
        return self._repo.delete(note_id)