import pytest
from unittest.mock import patch, ANY
import pandas as pd
from infrastructure.ui.export_pdf import generate_pdf_export


@pytest.fixture
def mock_fpdf():
    with patch('infrastructure.ui.export_pdf._ReportePDF') as mock:
        instance = mock.return_value
        instance.output.return_value = b'PDF_CONTENT'
        # Default geometry mocks
        instance.w = 210
        instance.l_margin = 10
        instance.r_margin = 10
        instance.h = 297
        instance.b_margin = 10
        instance.get_y.return_value = 20
        # String width valid value to avoid div by zero
        instance.get_string_width.return_value = 10
        yield mock


@pytest.fixture
def mock_plotly():
    with patch('infrastructure.ui.export_pdf.pio') as mock:
        mock.to_image.return_value = b'IMAGE_BYTES'
        yield mock


def test_generate_pdf_export_success(mock_fpdf, mock_plotly):
    df = pd.DataFrame({
        'Clasificacion': ['A', 'B'],
        'comentarios': ['c1', 'c2'],
        'calificacion': ['5', '1']
    })

    result = generate_pdf_export(df)

    assert result == b'PDF_CONTENT'
    mock_fpdf.return_value.add_page.assert_called()
    mock_plotly.to_image.assert_called()


def test_generate_pdf_export_empty_df():
    with pytest.raises(ValueError, match="El DataFrame está vacío"):
        generate_pdf_export(pd.DataFrame())


def test_generate_pdf_export_handles_exception(mock_fpdf):
    # Simulate an error during generation (e.g. in add_page)
    mock_fpdf.return_value.add_page.side_effect = [Exception("Planned Error"), None]

    result = generate_pdf_export(pd.DataFrame({'a': [1]}))

    # Should return an error PDF content instead of raising
    # The error handler creates a NEW FPDF instance
    # We need to verify we got bytes back
    assert result == b'PDF_CONTENT'


def test_generate_pdf_with_charts(mock_fpdf, mock_plotly):
    df = pd.DataFrame({
        'Clasificacion': ['Positive', 'Negative'],
        'comentarios': ['Great', 'Bad'],
        'num_palabras': [1, 1]
    })

    generate_pdf_export(df)

    # Verify chart generation calls
    # Should generate pie, bar, and histogram
    assert mock_plotly.to_image.call_count == 3


def test_generate_pdf_comments_pagination(mock_fpdf, mock_plotly):
    # Setup dataframe with enough comments to trigger pagination
    df = pd.DataFrame({
        'Clasificacion': ['A'] * 20,
        'comentarios': ['Comment'] * 20
    })

    # Mock geometry to force pagination
    mock_fpdf.return_value.get_y.side_effect = [280] * 100  # Near bottom

    generate_pdf_export(df)

    # Should call add_page more than once (initial + pagination)
    assert mock_fpdf.return_value.add_page.call_count >= 2


def test_generate_pdf_custom_comments_list(mock_fpdf):
    df = pd.DataFrame({'a': [1]})
    comments_df = pd.DataFrame({'comentarios': ['Specific Comment'], 'Clasificacion': ['A']})

    generate_pdf_export(df, comments_df=comments_df)

    # Verification would be inspecting the FPDF calls to see if "Specific Comment" was rendered
    # We can check specific cell calls if needed, but integration logic is main goal here
    mock_fpdf.return_value.multi_cell.assert_any_call(ANY, ANY, "Specific Comment", border=0)
