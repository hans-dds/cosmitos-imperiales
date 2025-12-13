import pytest
from unittest.mock import MagicMock, patch, mock_open
from adapters.email_sender_adapter import SmtpEmailSender
import smtplib


@pytest.fixture
def email_config():
    return {
        'smtp_server': 'localhost',
        'smtp_port': 587,
        'smtp_user': 'user',
        'smtp_password': 'password',
        'email_from': 'test@example.com'
    }


@pytest.fixture
def sender(email_config):
    return SmtpEmailSender(**email_config)


@patch('smtplib.SMTP')
def test_send_email_success_with_auth(mock_smtp, sender):
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    to_emails = ["recipient@example.com"]
    subject = "Test Subject"
    body = "Test Body"

    success = sender.send_email(to_emails, subject, body)

    assert success is True
    mock_smtp.assert_called_with('localhost', 587)
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_with('user', 'password')
    mock_server.send_message.assert_called_once()

    # Check message content loosely
    args, _ = mock_server.send_message.call_args
    msg = args[0]
    assert msg['Subject'] == subject
    assert msg['From'] == 'test@example.com'
    assert msg['To'] == 'recipient@example.com'


@patch('smtplib.SMTP')
def test_send_email_success_no_auth(mock_smtp):
    sender = SmtpEmailSender('localhost', 25, '', '', 'test@example.com')
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    success = sender.send_email(["to@example.com"], "Subj", "Body")

    assert success is True
    mock_server.login.assert_not_called()
    mock_server.send_message.assert_called_once()


def test_send_email_no_recipients(sender):
    success = sender.send_email([], "Subj", "Body")
    assert success is False


@patch('smtplib.SMTP')
def test_send_email_connection_error(mock_smtp, sender):
    mock_smtp.side_effect = Exception("Connection refused")

    success = sender.send_email(["to@example.com"], "Subj", "Body")

    assert success is False


@patch('smtplib.SMTP')
def test_send_email_login_error(mock_smtp, sender):
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server
    mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, "Auth fail")

    success = sender.send_email(["to@example.com"], "Subj", "Body")

    assert success is False


@patch('smtplib.SMTP')
def test_send_email_with_pdf_attachment(mock_smtp, sender):
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    with patch('builtins.open', mock_open(read_data=b'PDF_BYTES')), \
            patch('os.path.basename', return_value="report.pdf"):

        success = sender.send_email(
            ["to@example.com"],
            "Subj",
            "Body",
            attachment_path="/path/to/report.pdf"
        )

        assert success is True
        mock_server.send_message.assert_called_once()

        args, _ = mock_server.send_message.call_args
        msg = args[0]
        # Check attachment exists
        assert len(msg.get_payload()) == 2  # Text part + Attachment part
        attachment = msg.get_payload()[1]
        assert attachment.get_content_type() == 'application/pdf'
        assert attachment.get_filename() == 'report.pdf'


@patch('smtplib.SMTP')
def test_send_email_with_excel_attachment(mock_smtp, sender):
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    with patch('builtins.open', mock_open(read_data=b'XLSX_BYTES')), \
            patch('os.path.basename', return_value="data.xlsx"):

        success = sender.send_email(
            ["to@example.com"],
            "Subj",
            "Body",
            attachment_path="/path/to/data.xlsx"
        )

        assert success is True

        args, _ = mock_server.send_message.call_args
        msg = args[0]
        attachment = msg.get_payload()[1]
        assert attachment.get_content_type() == (
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )


@patch('smtplib.SMTP')
def test_send_email_attachment_error(mock_smtp, sender):
    # Mock open to raise exception
    with patch('builtins.open', side_effect=FileNotFoundError("File not found")):

        success = sender.send_email(
            ["to@example.com"],
            "Subj",
            "Body",
            attachment_path="missing.pdf"
        )

        # Should fail because attachment logic catches exception and returns false
        assert success is False
        mock_smtp.assert_not_called()  # Should return before connecting
