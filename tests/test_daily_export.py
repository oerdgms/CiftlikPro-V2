import unittest
from unittest.mock import patch
from datetime import date
import io
from pypdf import PdfReader
from test_reports_import import server

class DailyExportTests(unittest.TestCase):
    def test_pdf_and_print_unicode_escape_and_empty(self):
        rows=[{'date':'2026-10-01','subject':'TR123 <test>','task':'Aşı','detail':'Şap & kontrol','status':'Bugün'}]
        with patch.object(server,'farm_profile',return_value={'farm_name':'Çiftlik'}):
            pdf=server.dashboard_tasks_pdf(rows,'today')
            text=''.join(p.extract_text() for p in PdfReader(io.BytesIO(pdf)).pages)
            self.assertIn('Şap & kontrol',text)
            self.assertIn('Bugün',text)
            html=server.dashboard_tasks_print(rows,'today')
            self.assertIn('&lt;test&gt;',html)
            self.assertNotIn('<test>',html)
            empty=server.dashboard_tasks_pdf([],'today')
            self.assertIn('bekleyen görev',PdfReader(io.BytesIO(empty)).pages[0].extract_text())

    def test_task_filter_invalid_fallback(self):
        server.init_db()
        with server.db() as c:
            c.execute("insert into health(kind,product,next_date) values('Kontrol','Dışa aktarım testi','2026-10-01')")
        try:
            rows=server.dashboard_export_tasks('all',date(2026,10,1))
            self.assertEqual(rows,server.dashboard_export_tasks('invalid',date(2026,10,1)))
            for state in ('overdue','today','upcoming'):
                self.assertEqual([r for r in rows if r['state']==state],server.dashboard_export_tasks(state,date(2026,10,1)))
        finally:
            with server.db() as c:c.execute("delete from health where product='Dışa aktarım testi'")
