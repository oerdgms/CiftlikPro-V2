import io
import threading
import unittest
import urllib.request
from datetime import date,timedelta
from unittest.mock import patch
from pypdf import PdfReader
from test_reports_import import server

class HealthWorkspaceTests(unittest.TestCase):
    def test_upcoming_includes_all_sources_and_print_uses_health_filters(self):
        server.init_db();today=date.today();due=(today+timedelta(days=3)).isoformat();ids={}
        with server.db() as c:
            ids['animal']=c.execute("insert into animals(tag,gender,status) values('TRHEALTHAI','Dişi','Aktif')").lastrowid
            insemination=(today+timedelta(days=3)-timedelta(days=210)).isoformat()
            ids['preg']=c.execute("insert into inseminations(animal_id,insemination_date,pregnancy_result,due_date) values(?,?,'Pozitif',?)",(ids['animal'],insemination,(today+timedelta(days=73)).isoformat())).lastrowid
            ids['course']=c.execute("insert into health_courses(kind,product,scope_type,start_date,created_at) values('Aşı','AI Şap <plan>','single',?,?)",(due,due)).lastrowid
            c.execute('insert into health_tasks(course_id,animal_id,planned_date) values(?,?,?)',(ids['course'],ids['animal'],due))
            c.execute("insert into health_tasks(course_id,animal_id,planned_date,status) values(?,?,?,'Yapıldı')",(ids['course'],ids['animal'],due))
            # More than the old four-row Dashboard limit.
            for i in range(6):c.execute("insert into health(animal_id,kind,product,next_date) values(?,'Kontrol',?,?)",(ids['animal'],'AI Eski '+str(i),due))
        server.SESSIONS['health-ai']={'username':'admin','role':'admin'}
        http=server.QuietThreadingHTTPServer(('127.0.0.1',0),server.App)
        threading.Thread(target=http.serve_forever,daemon=True).start()
        def request(route):
            req=urllib.request.Request(f'http://127.0.0.1:{http.server_port}'+route,headers={'Cookie':'sid=health-ai'})
            with urllib.request.urlopen(req,timeout=20) as response:return response.read()
        try:
            upcoming=server.health_export_tasks('upcoming','TRHEALTHAI')
            self.assertEqual(len(upcoming),8)
            self.assertEqual({r['source'] for r in upcoming},{'legacy','course','pregnancy'})
            self.assertFalse(server.health_export_tasks('today','TRHEALTHAI'))
            with patch.object(server,'license_status',return_value=(True,{},'')):
                dashboard=request('/').decode()
                self.assertIn('AI Eski 5',dashboard)
                self.assertIn('7. Ay Gebelik Aşısı',dashboard)
                self.assertIn('AI Şap &lt;plan&gt;',dashboard)
                self.assertNotIn('data-task-export=',dashboard)
                health=request('/health?filter=upcoming&search=TRHEALTHAI').decode()
                self.assertIn('health/tasks.pdf',health)
                self.assertIn('health-view-switch',health)
                self.assertIn('hotfix122az-health-action-menu',health)
                self.assertIn("toggle.type='button'",health)
                self.assertIn("toggle.setAttribute('aria-expanded','false')",health)
                self.assertIn("controls.hidden=true",health)
                self.assertNotIn("const more=document.createElement('details')",health)
                self.assertIn('data-health-user="admin"',health)
                self.assertIn("mode='agenda'",health)
                self.assertIn('data-health-date="'+due+'"',health)
                pdf=request('/health/tasks.pdf?filter=upcoming&search=TRHEALTHAI')
                text=' '.join(p.extract_text() for p in PdfReader(io.BytesIO(pdf)).pages)
                self.assertIn('Sağlık İş Planı',text);self.assertIn('8 görev',text)
                self.assertIn('7. Ay Gebelik Aşısı',text);self.assertNotIn('Vadeli ödeme',text)
                printed=request('/health/tasks/print?filter=upcoming&search=TRHEALTHAI').decode()
                self.assertIn('AI Şap &lt;plan&gt;',printed)
                self.assertIn('search=TRHEALTHAI',printed)
                empty=request('/health/tasks.pdf?filter=today&search=TRHEALTHAI')
                self.assertIn('0 görev',PdfReader(io.BytesIO(empty)).pages[0].extract_text())
        finally:
            http.shutdown();http.server_close();server.SESSIONS.pop('health-ai',None)
            with server.db() as c:
                c.execute('delete from health_tasks where course_id=?',(ids['course'],));c.execute('delete from health_courses where id=?',(ids['course'],))
                c.execute('delete from health where animal_id=?',(ids['animal'],));c.execute('delete from inseminations where id=?',(ids['preg'],));c.execute('delete from animals where id=?',(ids['animal'],))
