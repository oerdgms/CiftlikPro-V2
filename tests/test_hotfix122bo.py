import tempfile, threading, unittest, urllib.parse, urllib.request
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch
from test_reports_import import server

class Hotfix122BOTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.db_patch=patch.object(server,'DB',Path(self.temp.name)/'test.db'); self.db_patch.start(); server.init_db()
        server.SESSIONS['bo-test']={'username':'admin','role':'admin'}
        self.http=server.QuietThreadingHTTPServer(('127.0.0.1',0),server.App); threading.Thread(target=self.http.serve_forever,daemon=True).start()
    def tearDown(self):
        self.http.shutdown(); self.http.server_close(); server.SESSIONS.pop('bo-test',None); self.db_patch.stop(); self.temp.cleanup()
    def get(self,path):
        req=urllib.request.Request(f'http://127.0.0.1:{self.http.server_port}{path}',headers={'Cookie':'sid=bo-test'})
        with patch.object(server,'license_status',return_value=(True,{},'')):
            with urllib.request.urlopen(req,timeout=20) as r:return r.read().decode('utf-8'),r.geturl()
    def post(self,path,data):
        req=urllib.request.Request(f'http://127.0.0.1:{self.http.server_port}{path}',data=urllib.parse.urlencode(data).encode(),method='POST',headers={'Cookie':'sid=bo-test','Content-Type':'application/x-www-form-urlencoded'})
        with patch.object(server,'license_status',return_value=(True,{},'')):
            with urllib.request.urlopen(req,timeout=20) as r:return r.read().decode('utf-8'),r.geturl()
    def add_female(self,tag):
        with server.db() as c:return c.execute("insert into animals(tag,gender,status,paddock) values(?,'Dişi','Aktif','SA1')",(tag,)).lastrowid
    def test_postpartum_lifecycle(self):
        fresh=self.add_female('TRBOFRESH'); control=self.add_female('TRBOCTRL'); ready=self.add_female('TRBOREADY')
        with server.db() as c:
            for aid,days,calf in ((fresh,20,'CF1'),(control,45,'CF2'),(ready,70,'CF3')):
                c.execute("insert into calves(tag,mother_id,birth_date,gender,status) values(?,?,?,'Dişi','Aktif')",(calf,aid,(date.today()-timedelta(days=days)).isoformat()))
            self.assertEqual(server.smart_reproduction_state(c,fresh)['code'],'fresh')
            self.assertEqual(server.smart_reproduction_state(c,control)['code'],'postpartum_control')
            self.assertEqual(server.smart_reproduction_state(c,ready)['code'],'ready')
    def test_dry_due_mark_and_clear_on_birth(self):
        aid=self.add_female('TRBODRY'); ins=date.today()-timedelta(days=220); due=ins+timedelta(days=280)
        with server.db() as c:
            iid=c.execute("insert into inseminations(animal_id,attempt,insemination_date,pregnancy_result,due_date) values(?,1,?,'Pozitif',?)",(aid,ins.isoformat(),due.isoformat())).lastrowid
            self.assertEqual(server.smart_reproduction_state(c,aid)['code'],'dry_due')
        self.post('/reproduction/dry',{'animal_id':aid,'dry_date':date.today().isoformat(),'return_to':'/reproduction-center'})
        with server.db() as c:
            self.assertEqual(server.smart_reproduction_state(c,aid)['code'],'dry')
            self.assertEqual(c.execute('select dry_since from animals where id=?',(aid,)).fetchone()['dry_since'],date.today().isoformat())
            server.close_pregnancy_after_birth(c,aid,date.today().isoformat())
            self.assertEqual(c.execute('select dry_since from animals where id=?',(aid,)).fetchone()['dry_since'],'')
    def test_individual_estrus_prediction(self):
        aid=self.add_female('TRBOEST')
        start=date.today()-timedelta(days=42)
        with server.db() as c:
            for i,d in enumerate((0,20,41)):
                c.execute("insert into estrus_records(animal_id,estrus_date,created_at) values(?,?,?)",(aid,(start+timedelta(days=d)).isoformat(),date.today().isoformat()))
            profile=server.estrus_cycle_profile(c,aid)
        self.assertEqual(profile['source'],'bireysel'); self.assertIn(profile['cycle_days'],(20,21))
        self.assertTrue(profile['next_center'])
    def test_reproduction_center_has_smart_groups_and_settings(self):
        html,_=self.get('/reproduction-center')
        for text in ('Taze','Üreme Kontrolü','Tohumlamaya Hazır','Kuruya Çıkar','Kuru','Üreme Ayarları'):
            self.assertIn(text,html)
        self.assertIn('data-repro-life=',html)
    def test_settings_are_editable(self):
        self.post('/reproduction-settings',{'fresh_days':'28','postpartum_control_day':'40','vwp_day':'55','dry_days_before_due':'58','closeup_days_before_due':'20','birth_alert_days_before_due':'6'})
        cfg=server.reproduction_settings(); self.assertEqual(cfg['fresh_days'],28); self.assertEqual(cfg['vwp_day'],55); self.assertEqual(cfg['dry_days_before_due'],58)
    def test_export_supports_smart_category(self):
        aid=self.add_female('TRBOEXPORT'); ins=date.today()-timedelta(days=222); due=ins+timedelta(days=280)
        with server.db() as c:c.execute("insert into inseminations(animal_id,attempt,insemination_date,pregnancy_result,due_date) values(?,1,?,'Pozitif',?)",(aid,ins.isoformat(),due.isoformat()))
        html,_=self.get('/reproduction-center/print?stage=dry_due')
        self.assertIn('Kuruya Çıkarılacak',html); self.assertIn('TRBOEXPORT',html)
    def test_version(self):
        self.assertEqual(server.APP_VERSION,'3.9.23 DEV4 Hotfix1.22bp'); self.assertEqual(server.APP_LABEL,'v3.9.23 DEV4 Hotfix1.22bp')

if __name__=='__main__':unittest.main()
