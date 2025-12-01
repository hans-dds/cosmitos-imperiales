import os
import pandas as pd

from use_cases.save_report_use_case import SaveReportUseCase
from use_cases.list_reports_use_case import ListReportsUseCase


class FakeRepo:
    def __init__(self):
        self.rows = []
        self.next_id = 1

    def save(self, analysis_name, report_format, file_path):
        self.rows.append({
            'id': self.next_id,
            'analysis_name': analysis_name,
            'report_format': report_format,
            'file_path': file_path,
            'created_at': '2025-11-30 00:00:00'
        })
        self.next_id += 1
        return True, "Reporte guardado en historial"

    def list(self):
        return list(self.rows)

    def get(self, report_id):
        for r in self.rows:
            if r['id'] == report_id:
                return r
        return None


def test_save_report_pdf(tmp_path):
    repo = FakeRepo()
    use_case = SaveReportUseCase(report_repository=repo, reports_base_dir=str(tmp_path))
    df = pd.DataFrame({'comentarios': ['a'], 'calificacion': [1.0], 'Clasificacion': ['Positivo']})
    ok, msg, path = use_case.execute('mi analisis', df, 'pdf')
    assert ok is True
    assert os.path.exists(path)
    assert path.endswith('.pdf')


def test_save_report_excel(tmp_path):
    repo = FakeRepo()
    use_case = SaveReportUseCase(report_repository=repo, reports_base_dir=str(tmp_path))
    df = pd.DataFrame({'comentarios': ['a'], 'calificacion': [1.0], 'Clasificacion': ['Positivo']})
    ok, msg, path = use_case.execute('mi analisis', df, 'excel')
    assert ok is True
    assert os.path.exists(path)
    assert path.endswith('.xlsx')


def test_list_reports():
    repo = FakeRepo()
    repo.save('a', 'pdf', '/x')
    repo.save('b', 'excel', '/y')
    lister = ListReportsUseCase(report_repository=repo)
    items = lister.execute()
    assert len(items) == 2
    assert items[0]['analysis_name'] == 'a'
