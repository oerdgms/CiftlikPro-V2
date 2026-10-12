import tempfile
import threading
import unittest
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from unittest.mock import patch

from test_reports_import import server


class Hotfix122CFTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(server, 'DB', Path(self.temp.name) / 'test.db')
        self.db_patch.start()
        server.init_db()
        with server.db() as connection:
            mother_id = connection.execute(
                "insert into animals(tag,nickname,gender,status) values('TRCFMOTHER','Anne','Dişi','Aktif')"
            ).lastrowid
            self.calf_id = connection.execute(
                """insert into calves(tag,mother_id,nickname,birth_date,gender,status,promoted_animal_id,purchase_price)
                   values('TRCF000001',?,'Satılık Buzağı',?,'Erkek','Aktif',null,1500)""",
                (mother_id, date.today().isoformat()),
            ).lastrowid
        server.SESSIONS['cf-test'] = {'username': 'admin', 'role': 'admin'}
        self.http = server.QuietThreadingHTTPServer(('127.0.0.1', 0), server.App)
        threading.Thread(target=self.http.serve_forever, daemon=True).start()

    def tearDown(self):
        self.http.shutdown()
        self.http.server_close()
        server.SESSIONS.pop('cf-test', None)
        self.db_patch.stop()
        self.temp.cleanup()

    def request(self, path, data=None):
        payload = urllib.parse.urlencode(data).encode() if data is not None else None
        request = urllib.request.Request(
            f'http://127.0.0.1:{self.http.server_port}{path}',
            data=payload,
            headers={'Cookie': 'sid=cf-test'},
        )
        with patch.object(server, 'license_status', return_value=(True, {}, '')):
            with urllib.request.urlopen(request, timeout=20) as response:
                return response.read().decode('utf-8'), response.geturl()

    def test_finance_lists_active_calves_for_calf_sale(self):
        html, _ = self.request('/finance')
        self.assertIn('id="calfSaleBox"', html)
        self.assertIn('name="calf_ids"', html)
        self.assertIn('TRCF000001', html)
        self.assertIn('isCalfSaleFinance', html)

    def test_calf_sale_creates_linked_income_and_archives_calf(self):
        html, final_url = self.request('/finance', {
            'tx_date': date.today().isoformat(),
            'tx_type': 'Gelir',
            'category': 'Buzağı Satışı',
            'amount': '12.500',
            'payment_method': 'Nakit',
            'calf_ids': str(self.calf_id),
            'description': 'Test alıcısı',
        })
        self.assertIn('/archive/sold', final_url)
        self.assertIn('TRCF000001', html)
        self.assertIn('Buzağı', html)
        with server.db() as connection:
            finance = connection.execute(
                "select * from finance where category='Buzağı Satışı' and calf_id=?",
                (self.calf_id,),
            ).fetchone()
            calf = connection.execute('select * from calves where id=?', (self.calf_id,)).fetchone()
        self.assertIsNotNone(finance)
        self.assertIsNone(finance['animal_id'])
        self.assertEqual(finance['animal_status_action'], 'Satıldı')
        self.assertAlmostEqual(float(finance['amount']), 12500.0)
        self.assertEqual(calf['status'], 'Satıldı')
        self.assertAlmostEqual(float(calf['sold_price']), 12500.0)

    def test_deleting_sale_reactivates_calf(self):
        self.request('/finance', {
            'tx_date': date.today().isoformat(), 'tx_type': 'Gelir',
            'category': 'Buzağı Satışı', 'amount': '5000',
            'payment_method': 'Nakit', 'calf_ids': str(self.calf_id),
        })
        with server.db() as connection:
            finance_id = connection.execute(
                "select id from finance where calf_id=? and category='Buzağı Satışı'",
                (self.calf_id,),
            ).fetchone()['id']
        self.request('/finance/delete', {'id': finance_id})
        with server.db() as connection:
            calf = connection.execute('select status,sold_price from calves where id=?', (self.calf_id,)).fetchone()
        self.assertEqual(calf['status'], 'Aktif')
        self.assertAlmostEqual(float(calf['sold_price']), 0.0)


if __name__ == '__main__':
    unittest.main()
