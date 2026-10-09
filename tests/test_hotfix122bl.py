import tempfile, threading, unittest, urllib.request
from pathlib import Path
from unittest.mock import patch
from datetime import date, timedelta
from test_reports_import import server

class Hotfix122BLTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.db_patch=patch.object(server,'DB',Path(self.temp.name)/'test.db'); self.db_patch.start()
        server.init_db()
        with server.db() as c:
            for i in range(1,7):
                c.execute("insert into animals(tag,gender,status,paddock) values(?,'Dişi','Aktif','SA1')",(f'TRBL{i:03d}',))
            aid=c.execute("select id from animals where tag='TRBL006'").fetchone()['id']
            # Old estrus record => active takip yok, but this animal is not 'never processed'.
            c.execute("insert into estrus_records(animal_id,estrus_date,signs,notes,created_at) values(?,?,?,?,?)",(aid,(date.today()-timedelta(days=120)).isoformat(),'','',date.today().isoformat()))
        server.SESSIONS['bl-test']={'username':'admin','role':'admin'}
        self.http=server.QuietThreadingHTTPServer(('127.0.0.1',0),server.App)
        threading.Thread(target=self.http.serve_forever,daemon=True).start()
    def tearDown(self):
        self.http.shutdown(); self.http.server_close(); server.SESSIONS.pop('bl-test',None)
        self.db_patch.stop(); self.temp.cleanup()
    def render(self,path='/reproduction-center'):
        req=urllib.request.Request(f'http://127.0.0.1:{self.http.server_port}{path}',headers={'Cookie':'sid=bl-test'})
        with patch.object(server,'license_status',return_value=(True,{},'')):
            with urllib.request.urlopen(req,timeout=20) as r: return r.read().decode()
    def test_single_empty_group_replaces_duplicate_unprocessed_filter(self):
        html=self.render()
        self.assertIn('Boş / İşlem Bekleyen 6 hayvan: 5 işlem yapılmamış, 1 yeniden işlem bekleyen',html)
        self.assertNotIn('data-repro-filter="unprocessed"',html)
        self.assertNotIn('＋ İşlem Yapılmamış <b>',html)
        self.assertIn('İşlem Yapılmamış',html)
        self.assertIn('İşlem Bekleyen',html)
    def test_legacy_unprocessed_url_maps_to_empty_group(self):
        html=self.render('/reproduction-center?stage=unprocessed')
        self.assertIn('data-repro-section="empty"',html)
        self.assertNotIn('data-repro-filter="unprocessed"',html)
    def test_version(self):
        self.assertEqual(server.APP_VERSION,'3.9.23 DEV4 Hotfix1.22cd')

if __name__=='__main__': unittest.main()
