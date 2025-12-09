import pytest
from unittest.mock import MagicMock, patch
import os

# Mock settings before importing the container to avoid side effects during import
with patch('infrastructure.config.settings') as mock_settings:
    mock_settings.DB_HOST = 'localhost'
    mock_settings.DB_PORT = 3306
    mock_settings.DB_USER = 'user'
    mock_settings.DB_PASSWORD = 'password'
    mock_settings.DB_NAME = 'db'
    mock_settings.CSV_BASE_DIR = '/tmp'
    mock_settings.EXPERIMENTS_DIR = '/tmp'
    mock_settings.SMTP_SERVER = 'smtp.test'
    mock_settings.SMTP_PORT = 587
    mock_settings.SMTP_USER = 'user'
    mock_settings.SMTP_PASSWORD = 'pass'
    mock_settings.EMAIL_FROM = 'test@test.com'
    mock_settings.EXCEL_REQUIRED_SHEETS = ['Sheet1']
    mock_settings.APP_TITLE = "Test App"
    
    # We also need to mock the adapters that the container initializes in __init__
    # to avoid real DB connections or file operations during test instantiation
    with patch('infrastructure.dependency_injection_container.SQLandCSVAnalysisRepository'), \
         patch('infrastructure.dependency_injection_container.SQLReportRepository'), \
         patch('infrastructure.dependency_injection_container.JoblibSentimentAnalyzer'), \
         patch('infrastructure.dependency_injection_container.PandasDataCleaner'), \
         patch('infrastructure.dependency_injection_container.PandasFileReader'), \
         patch('infrastructure.dependency_injection_container.SmtpEmailSender'), \
         patch('infrastructure.dependency_injection_container.SQLNoteRepository'), \
         patch('infrastructure.dependency_injection_container.GeminiAdvisorAdapter'):
         
        from infrastructure.dependency_injection_container import Container, container

@pytest.fixture
def mock_container_deps():
    """Patches all external dependencies instantiated by Container.__init__"""
    with patch('infrastructure.dependency_injection_container.SQLandCSVAnalysisRepository') as repo, \
         patch('infrastructure.dependency_injection_container.SQLReportRepository') as report_repo, \
         patch('infrastructure.dependency_injection_container.JoblibSentimentAnalyzer') as analyzer, \
         patch('infrastructure.dependency_injection_container.PandasDataCleaner') as cleaner, \
         patch('infrastructure.dependency_injection_container.PandasFileReader') as reader, \
         patch('infrastructure.dependency_injection_container.SmtpEmailSender') as sender, \
         patch('infrastructure.dependency_injection_container.SQLNoteRepository') as note_repo, \
         patch('infrastructure.dependency_injection_container.GeminiAdvisorAdapter') as advisor:
        yield {
            'repo': repo,
            'report_repo': report_repo,
            'analyzer': analyzer,
            'cleaner': cleaner,
            'reader': reader,
            'sender': sender,
            'note_repo': note_repo,
            'advisor': advisor
        }

def test_container_initialization(mock_container_deps):
    """Test that container initializes all adapters with correct config."""
    c = Container()
    
    # Check Analysis Repository init
    mock_container_deps['repo'].assert_called()
    
    # Check Sentiment Analyzer init
    mock_container_deps['analyzer'].assert_called()
    
    # Check Report Repository init
    mock_container_deps['report_repo'].assert_called()

def test_use_cases_creation(mock_container_deps):
    """Test that all use case properties return valid instances."""
    c = Container()
    
    # Just accessing the property should create the use case without error
    # We verify it's not None and checks types if strictly needed (implicit by import)
    
    assert c.process_file_use_case is not None
    assert c.list_analyses_use_case is not None
    assert c.load_analysis_use_case is not None
    assert c.delete_analysis_use_case is not None
    assert c.read_file_use_case is not None
    assert c.prepare_analysis_display_use_case is not None
    assert c.send_results_email_use_case is not None
    assert c.save_report_use_case is not None
    assert c.list_reports_use_case is not None
    assert c.clear_reports_history_use_case is not None
    assert c.delete_report_use_case is not None
    assert c.update_sentiment_use_case is not None
    assert c.manage_notes_use_case is not None
    assert c.get_suggestions_use_case is not None
    
def test_streamlit_controller_creation(mock_container_deps):
    """Test that streamlit_controller is created with all dependencies."""
    c = Container()
    controller = c.streamlit_controller
    assert controller is not None
    # We could assert that specific dependencies inside controller are the ones from the container
    # but that would require inspecting private attributes.
    # The fact it instantiates without error is the main regression test here.
