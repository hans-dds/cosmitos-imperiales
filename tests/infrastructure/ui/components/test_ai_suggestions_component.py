import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
from infrastructure.ui.components.ai_suggestions_component import AISuggestionsComponent
from infrastructure.ui.controllers.streamlit_controller import StreamlitController


@pytest.fixture
def mock_controller():
    return MagicMock(spec=StreamlitController)


@pytest.fixture
def component():
    return AISuggestionsComponent()


@pytest.fixture
def mock_streamlit():
    with patch('infrastructure.ui.components.ai_suggestions_component.st') as mock_st:
        # Defaults for context managers
        mock_st.spinner.return_value.__enter__.return_value = None
        yield mock_st


def test_render_initial_state(component, mock_controller, mock_streamlit):
    df = pd.DataFrame()
    mock_streamlit.button.return_value = False

    component.render(mock_controller, df)

    mock_streamlit.markdown.assert_any_call("---")
    mock_streamlit.subheader.assert_called_with("Sugerencias de Mejora (AI)")
    mock_streamlit.write.assert_called()
    mock_streamlit.button.assert_called_with("Generar Recomendaciones con IA")

    # Should not call controller if button not clicked
    mock_controller.get_ai_suggestions.assert_not_called()


def test_render_button_clicked(component, mock_controller, mock_streamlit):
    df = pd.DataFrame({'a': [1]})
    mock_streamlit.button.return_value = True
    mock_controller.get_ai_suggestions.return_value = "**Suggestions**"

    component.render(mock_controller, df)

    mock_streamlit.button.assert_called_with("Generar Recomendaciones con IA")
    mock_streamlit.spinner.assert_called_with("Consultando a Gemini...")
    mock_controller.get_ai_suggestions.assert_called_with(df)
    mock_streamlit.markdown.assert_called_with("**Suggestions**")
