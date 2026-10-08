import tempfile, threading, unittest, urllib.request
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch
from test_reports_import import server

class Hotfix122BNTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.db_patch=patch.object(server,'DB',Path(self.temp.name)/'test.db'); self.db_patch.start(); server.init_db()
        with server.db() as c:
            self.preg=c.execute("insert into animals(tag,nickname,gender,status,paddock,breed) values('TRBNP','Gebe','Dişi','Aktif','SA1','Simental')").lastrowid
            self.neg=c.execute("insert into animals(tag,nickname,gender,status,paddock,breed) values('TRBNN','Negatif','Dişi','Aktif','SA2','Simental')").lastrowid
            self.empty=c.execute("insert into animals(tag,nickname,gender,status,paddock,breed) values('TRBNE','Boş','Dişi','Aktif','SA3','Simental')").lastrowid
            d=(date.today()-timedelta(days=40)).isoformat()
            c.execute("insert into inseminations(animal_id,attempt,insemination_date,pregnancy_result,due_date) values(?,1,?,'Pozitif',?)",(self.preg,d,(date.today()+timedelta(days=240)).isoformat()))
            c.execute("insert into inseminations(animal_id,attempt,insemination_date,pregnancy_result,due_date) values(?,1,?,'Negatif','')",(self.neg,d))
            course=c.execute("insert into health_courses(kind,product,scope_type,start_date,dose_count,interval_days,cost_per_application,notes,created_at,active) values('Aşı','BN Aşı','multi',?,2,15,0,'rapor testi',?,1)",(date.today().isoformat(),date.today().isoformat())).lastrowid
            server.create_health_course_tasks(c,course,[(self.preg,None,'TRBNP'),(self.neg,None,'TRBNN')],'Aşı',date.today().isoformat(),0,'rapor testi',dose_count=2,interval_days=15)
        server.SESSIONS['bn-test']={'username':'admin','role':'admin'}
        self.http=server.QuietThreadingHTTPServer(('127.0.0.1',0),server.App); threading.Thread(target=self.http.serve_forever,daemon=True).start()
    def tearDown(self):
        self.http.shutdown(); self.http.server_close(); server.SESSIONS.pop('bn-test',None); self.db_patch.stop(); self.temp.cleanup()
    def get(self,path,binary=False):
        req=urllib.request.Request(f'http://127.0.0.1:{self.http.server_port}{path}',headers={'Cookie':'sid=bn-test'})
        with patch.object(server,'license_status',return_value=(True,{},'')):
            with urllib.request.urlopen(req,timeout=20) as r:
                data=r.read(); return data if binary else data.decode('utf-8')
    def test_reproduction_print_respects_category(self):
        html=self.get('/reproduction-center/print?stage=pregnant')
        self.assertIn('Üreme Sağlık Durum Raporu',html); self.assertIn('TRBNP',html); self.assertNotIn('TRBNN',html); self.assertNotIn('TRBNE',html)
        empty=self.get('/reproduction-center/print?stage=empty'); self.assertIn('TRBNE',empty); self.assertNotIn('TRBNP',empty)
    def test_reproduction_pdf_is_real_pdf(self):
        raw=self.get('/reproduction-center.pdf?stage=negative',True); self.assertTrue(raw.startswith(b'%PDF'))
    def test_health_plan_print_and_pdf(self):
        html=self.get('/health/plans/print?filter=all&search=BN%20A%C5%9F%C4%B1'); self.assertIn('İlaç &amp; Aşı Planları',html); self.assertIn('BN Aşı',html); self.assertIn('Çoklu Hayvan',html); self.assertIn('TRBNP',html)
        raw=self.get('/health/plans.pdf?filter=all&search=BN%20A%C5%9F%C4%B1',True); self.assertTrue(raw.startswith(b'%PDF'))
    def test_buttons_present(self):
        repro=self.get('/reproduction-center'); self.assertIn('bnReproPdf',repro); self.assertIn('bnReproPrint',repro)
        health=self.get('/health'); self.assertIn('bnHealthPlanPdf',health); self.assertIn('bnHealthPlanPrint',health)
    def test_version(self): self.assertEqual(server.APP_VERSION,'3.9.23 DEV4 Hotfix1.22br')

if __name__=='__main__': unittest.main()
