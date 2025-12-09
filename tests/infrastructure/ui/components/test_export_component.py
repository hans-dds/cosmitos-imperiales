import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from infrastructure.ui.components.export_component import ExportComponent


@pytest.fixture
def mock_controller():
    return MagicMock()


@pytest.fixture
def mock_streamlit():
    with patch('infrastructure.ui.components.export_component.st') as mock:
        mock.session_state = {}
        # Columns for download buttons
        col1, col2 = MagicMock(), MagicMock()
        mock.columns.return_value = [col1, col2]
        # Tabs
        tab1, tab2 = MagicMock(), MagicMock()
        mock.tabs.return_value = [tab1, tab2]

        yield mock


@pytest.fixture
def mock_exporters():
    with patch(
        'infrastructure.ui.components.export_component.generate_excel_export'
    ) as excel_mock, patch(
        'infrastructure.ui.components.export_component.generate_pdf_export'
    ) as pdf_mock, patch(
        'infrastructure.ui.components.export_component.apply_comments_filters'
    ) as filter_mock:

        excel_mock.return_value = b'EXCEL_DATA'
        pdf_mock.return_value = b'PDF_DATA'
        filter_mock.return_value = pd.DataFrame()

        yield {
            'excel': excel_mock,
            'pdf': pdf_mock,
            'filter': filter_mock
        }


@pytest.fixture
def mock_report_history():
    with patch('infrastructure.ui.components.export_component.ReportHistoryComponent') as mock:
        yield mock.return_value


def test_render_downloads_triggered(
        mock_controller, mock_streamlit, mock_exporters, mock_report_history):
    comp = ExportComponent(mock_controller)
    df = pd.DataFrame({'a': [1]})

    # Simulate user clicking both download buttons
    mock_streamlit.download_button.side_effect = [True, True]

    # Mock saving success
    mock_controller.handle_save_report.return_value = (True, "Saved", "path")

    comp.render(df, "analisis", {})

    # Verify export generation
    mock_exporters['excel'].assert_called_with(df)
    mock_exporters['pdf'].assert_called()

    # Verify controller save calls
    assert mock_controller.handle_save_report.call_count == 2

    # Verify history component render
    mock_report_history.render.assert_called_with(mock_controller)


def test_email_sending_success(mock_controller, mock_streamlit, mock_exporters):
    comp = ExportComponent(mock_controller)
    df = pd.DataFrame({'a': [1]})

    # Mock form inputs
    mock_streamlit.text_area.return_value = "test@example.com"
    mock_streamlit.radio.return_value = "PDF"
    # Submit button returns True
    mock_streamlit.form_submit_button.return_value = True

    # Mock download buttons returning False (no clicks)
    mock_streamlit.download_button.return_value = False

    # Mock sending success
    mock_controller.handle_send_email.return_value = (True, "Email sent")

    comp.render(df, "analisis", {})

    # Verify email sending
    mock_controller.handle_send_email.assert_called_with(
        to_emails=["test@example.com"],
        analysis_name="analisis",
        df=df,
        attachment_type="pdf",
        color_map={},
        comments_df=mock_exporters['filter'].return_value
    )
    mock_streamlit.success.assert_called()


def test_email_sending_no_valid_emails(mock_controller, mock_streamlit):
    comp = ExportComponent(mock_controller)
    df = pd.DataFrame({'a': [1]})

    # Empty email
    mock_streamlit.text_area.return_value = "   "
    mock_streamlit.form_submit_button.return_value = True
    mock_streamlit.download_button.return_value = False

    comp.render(df, "analisis", {})

    mock_streamlit.warning.assert_called()
    mock_controller.handle_send_email.assert_not_called()
