import tempfile
import threading
import unittest
import urllib.request
from pathlib import Path
from unittest.mock import patch

from test_reports_import import server


class Hotfix122BTTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(server, 'DB', Path(self.temp.name) / 'test.db')
        self.db_patch.start()
        server.init_db()
        with server.db() as c:
            c.execute("insert into animals(tag,nickname,gender,breed,paddock,status) values('TR583074660','Sarı Boynuzlu','Dişi','Simental','SA3','Aktif')")
            c.execute("insert into animals(tag,nickname,gender,breed,paddock,status) values('TR999999999','Başka Hayvan','Dişi','Holstein','SA1','Aktif')")
        server.SESSIONS['bt-test'] = {'username': 'admin', 'role': 'admin'}
        self.http = server.QuietThreadingHTTPServer(('127.0.0.1', 0), server.App)
        threading.Thread(target=self.http.serve_forever, daemon=True).start()

    def tearDown(self):
        self.http.shutdown()
        self.http.server_close()
        server.SESSIONS.pop('bt-test', None)
        self.db_patch.stop()
        self.temp.cleanup()

    def get(self, path):
        request = urllib.request.Request(
            f'http://127.0.0.1:{self.http.server_port}{path}',
            headers={'Cookie': 'sid=bt-test'},
        )
        with patch.object(server, 'license_status', return_value=(True, {}, '')):
            with urllib.request.urlopen(request, timeout=20) as response:
                return response.read().decode('utf-8')

    def test_herd_search_finds_partial_ear_tag(self):
        html = self.get('/all-animals?q=3074660')
        self.assertIn('TR583074660', html)
        self.assertNotIn('TR999999999', html)
        self.assertIn('1 hayvan · Tüm padoklar · 3074660', html)

    def test_herd_search_controls_are_injected(self):
        html = self.get('/all-animals')
        self.assertIn('hotfix122bt-herd-search', html)
        self.assertIn("submit.textContent='Ara'", html)
        self.assertIn('QR / 2D barkod tara', html)
        self.assertIn("file.setAttribute('capture','environment')", html)
        self.assertIn('850', html)

    def test_reproduction_modes_keep_existing_groups(self):
        html = self.get('/reproduction-center')
        self.assertIn('hotfix122bt-reproduction-modes', html)
        self.assertIn('Üreme Takibi', html)
        self.assertIn('Akıllı Gebelik', html)
        self.assertIn('repro-smart-kpis', html)
        self.assertIn('repro-stage-tabs', html)
        self.assertIn('bnReproPdf', html)

    def test_version(self):
        self.assertEqual(server.APP_VERSION, '3.9.23 DEV4 Hotfix1.22cd')
        self.assertEqual(server.APP_LABEL, 'v3.9.23 DEV4 Hotfix1.22cd')


if __name__ == '__main__':
    unittest.main()
