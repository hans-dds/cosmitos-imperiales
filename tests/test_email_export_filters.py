import unittest
from unittest.mock import MagicMock, patch
import pandas as pd

from use_cases.send_results_email_use_case import SendResultsEmailUseCase


class TestEmailExportFilters(unittest.TestCase):
    def setUp(self):
        self.email_sender = MagicMock()
        self.email_sender.send_email.return_value = True
        self.use_case = SendResultsEmailUseCase(self.email_sender)

    def test_excel_ignores_filtered_comments_df(self):
        df = pd.DataFrame({
            'comentarios': ['a', 'b', 'c'],
            'calificacion': [1, 2, 3],
            'Clasificacion': ['X', 'Y', 'Z'],
            'Fiabilidad': ['Alta', 'Media', 'Baja']
        })
        filtered = df.head(1)

        with patch('use_cases.send_results_email_use_case.generate_excel_export') as mock_excel:
            mock_excel.return_value = b'EXCEL'
            success, msg = self.use_case.execute(
                to_emails=['test@example.com'],
                analysis_name='Test',
                df=df,
                attachment_type='excel',
                comments_df=filtered,
            )
            self.assertTrue(success)
            # Debe usar el DataFrame completo (3 filas), ignorando filtrado
            args, kwargs = mock_excel.call_args
            passed_df = args[0]
            self.assertEqual(len(passed_df), 3)

    def test_pdf_uses_filtered_comments_df(self):
        df = pd.DataFrame({
            'comentarios': ['a', 'b'],
            'calificacion': [1, 2],
            'Clasificacion': ['X', 'Y'],
            'Fiabilidad': ['Alta', 'Media']
        })
        filtered = df[df['Clasificacion'] == 'X']
        color_map = {'X': '#000000', 'Y': '#111111'}

        with patch('use_cases.send_results_email_use_case.generate_pdf_export') as mock_pdf:
            mock_pdf.return_value = b'PDF'
            success, msg = self.use_case.execute(
                to_emails=['test@example.com'],
                analysis_name='Test',
                df=df,
                attachment_type='pdf',
                color_map=color_map,
                comments_df=filtered,
            )
            self.assertTrue(success)
            args, kwargs = mock_pdf.call_args
            # generate_pdf_export(df, color_map, comments_df=...)
            self.assertIn('comments_df', kwargs)
            self.assertEqual(len(kwargs['comments_df']), 1)


if __name__ == '__main__':
    unittest.main()
