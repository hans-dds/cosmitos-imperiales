import pytest
from unittest.mock import MagicMock, patch
from infrastructure.ui.components.notes_component import NotesComponent


@pytest.fixture
def mock_controller():
    return MagicMock()


@pytest.fixture
def mock_streamlit():
    with patch('infrastructure.ui.components.notes_component.st') as mock:
        yield mock


def test_render_no_notes(mock_controller, mock_streamlit):
    comp = NotesComponent()
    mock_controller.get_notes.return_value = []

    # Mock text_area and form submission return false initially
    mock_streamlit.form_submit_button.return_value = False

    comp.render(mock_controller, "analisis")

    mock_streamlit.info.assert_called_with("No hay notas guardadas para este reporte.")


def test_render_existing_notes_and_delete(mock_controller, mock_streamlit):
    comp = NotesComponent()
    mock_controller.get_notes.return_value = [
        {"id": 1, "created_at": "2023-01-01", "note_content": "Nota 1"}
    ]

    # Simulate delete button click for note 1
    def button_side_effect(*args, **kwargs):
        return kwargs.get("key") == "del_note_1"
    mock_streamlit.button.side_effect = button_side_effect

    # Ensure form submit is false
    mock_streamlit.form_submit_button.return_value = False

    mock_controller.delete_note.return_value = (True, "Deleted")

    comp.render(mock_controller, "analisis")

    # Verify note display
    mock_streamlit.expander.assert_called()
    mock_streamlit.write.assert_called_with("Nota 1")

    # Verify deletion
    mock_controller.delete_note.assert_called_with(1)
    mock_streamlit.rerun.assert_called()


def test_add_note_success(mock_controller, mock_streamlit):
    comp = NotesComponent()
    mock_controller.get_notes.return_value = []

    # Simulate form submission
    mock_streamlit.text_area.return_value = "Nueva nota content"
    mock_streamlit.form_submit_button.return_value = True

    mock_controller.add_note.return_value = (True, "Added")

    comp.render(mock_controller, "analisis")

    mock_controller.add_note.assert_called_with("analisis", "Nueva nota content")
    mock_streamlit.success.assert_called_with("Added")
    mock_streamlit.rerun.assert_called()


def test_add_note_failure(mock_controller, mock_streamlit):
    comp = NotesComponent()
    mock_controller.get_notes.return_value = []

    # Simulate form submission
    mock_streamlit.text_area.return_value = "Nueva nota content"
    mock_streamlit.form_submit_button.return_value = True

    mock_controller.add_note.return_value = (False, "Error adding")

    comp.render(mock_controller, "analisis")

    mock_streamlit.error.assert_called_with("Error adding")
