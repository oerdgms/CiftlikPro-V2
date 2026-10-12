import tempfile
import threading
import unittest
import urllib.request
from datetime import date
from pathlib import Path
from unittest.mock import patch

from test_reports_import import server


class Hotfix122CGTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(server, 'DB', Path(self.temp.name) / 'test.db')
        self.db_patch.start()
        server.init_db()
        with server.db() as connection:
            mother_id = connection.execute(
                "insert into animals(tag,nickname,gender,status) values('TRCGMOTHER','Anne','Dişi','Aktif')"
            ).lastrowid
            for index in range(3):
                connection.execute(
                    """insert into calves(tag,mother_id,nickname,birth_date,gender,status,promoted_animal_id)
                       values(?,?,?,?,?,'Aktif',null)""",
                    (
                        f'TRCG00000{index + 1}',
                        mother_id,
                        f'Aktif Buzağı {index + 1}',
                        date.today().isoformat(),
                        'Dişi' if index % 2 else 'Erkek',
                    ),
                )
        server.SESSIONS['cg-test'] = {'username': 'admin', 'role': 'admin'}
        self.http = server.QuietThreadingHTTPServer(('127.0.0.1', 0), server.App)
        threading.Thread(target=self.http.serve_forever, daemon=True).start()

    def tearDown(self):
        self.http.shutdown()
        self.http.server_close()
        server.SESSIONS.pop('cg-test', None)
        self.db_patch.stop()
        self.temp.cleanup()

    def request(self, path):
        request = urllib.request.Request(
            f'http://127.0.0.1:{self.http.server_port}{path}',
            headers={'Cookie': 'sid=cg-test'},
        )
        with patch.object(server, 'license_status', return_value=(True, {}, '')):
            with urllib.request.urlopen(request, timeout=20) as response:
                return response.read().decode('utf-8')

    def test_finance_renders_every_eligible_calf(self):
        html = self.request('/finance')
        self.assertEqual(html.count('class="bulk-row calf-sale-row"'), 3)
        self.assertIn('Satılacak Buzağılar <span class="pill">3 kayıt</span>', html)
        for index in range(3):
            self.assertIn(f'TRCG00000{index + 1}', html)

    def test_each_live_search_is_scoped_to_its_own_picker(self):
        html = self.request('/finance')
        self.assertIn("document.querySelectorAll('#bulkList .bulk-row')", html)
        self.assertIn("document.querySelectorAll('#calfSaleList .calf-sale-row')", html)
        self.assertIn("document.querySelectorAll('#milkList .milk-row')", html)
        self.assertNotIn("document.querySelectorAll('.bulk-row').forEach", html)


if __name__ == '__main__':
    unittest.main()
