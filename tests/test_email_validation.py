import unittest
from unittest.mock import MagicMock
import pandas as pd
from use_cases.send_results_email_use_case import SendResultsEmailUseCase

class TestEmailValidation(unittest.TestCase):

    def setUp(self):
        self.email_sender = MagicMock()
        self.use_case = SendResultsEmailUseCase(self.email_sender)
        self.df = pd.DataFrame()

    def test_valid_emails(self):
        to_emails = ["test@example.com", "user.name@domain.co.uk"]
        self.email_sender.send_email.return_value = True
        
        # Default excel
        success, message = self.use_case.execute(to_emails, "Analysis", self.df)
        self.assertTrue(success)
        self.email_sender.send_email.assert_called()
        args, kwargs = self.email_sender.send_email.call_args
        self.assertTrue(kwargs['attachment_path'].endswith('.xlsx'))

    def test_pdf_attachment(self):
        to_emails = ["test@example.com"]
        self.email_sender.send_email.return_value = True
        color_map = {"class": "color"}
        
        # Mock generate_pdf_export since it requires dependencies
        with unittest.mock.patch('use_cases.send_results_email_use_case.generate_pdf_export') as mock_pdf:
            mock_pdf.return_value = b"PDF CONTENT"
            
            success, message = self.use_case.execute(to_emails, "Analysis", self.df, attachment_type='pdf', color_map=color_map)
            
            self.assertTrue(success)
            self.email_sender.send_email.assert_called()
            args, kwargs = self.email_sender.send_email.call_args
            self.assertTrue(kwargs['attachment_path'].endswith('.pdf'))

    def test_invalid_email_format(self):
        to_emails = ["valid@example.com", "invalid-email", "no_at_sign.com"]
        
        success, message = self.use_case.execute(to_emails, "Analysis", self.df)
        
        self.assertFalse(success)
        self.assertIn("invalid-email", message)
        self.assertIn("no_at_sign.com", message)
        self.email_sender.send_email.assert_not_called()

    def test_empty_list(self):
        to_emails = []
        success, message = self.use_case.execute(to_emails, "Analysis", self.df)
        self.assertFalse(success)
        self.assertEqual(message, "La lista de correos está vacía.")

if __name__ == '__main__':
    unittest.main()
