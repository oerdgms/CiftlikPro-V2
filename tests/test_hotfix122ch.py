import tempfile
import threading
import unittest
import urllib.request
from pathlib import Path
from unittest.mock import patch

from test_reports_import import server


class Hotfix122CHTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(server, 'DB', Path(self.temp.name) / 'test.db')
        self.db_patch.start()
        server.init_db()

    def tearDown(self):
        self.db_patch.stop()
        self.temp.cleanup()

    def test_purchase_without_purchase_date_is_reconciled_to_expense(self):
        with server.db() as connection:
            animal_id = connection.execute(
                """insert into animals(tag,gender,status,purchase_date,purchase_price)
                   values('TRCH000001','Dişi','Satıldı','',45000)"""
            ).lastrowid
            finance_id = connection.execute(
                """insert into finance(
                       tx_date,tx_type,category,amount,description,payment_method,
                       animal_id,created_at
                   ) values('2026-07-27','Gelir','Hayvan Alımı',45000,?,'Nakit',?,'2026-07-27T12:00:00')""",
                ('TRCH000001', animal_id),
            ).lastrowid

        # Gerçek yükseltme akışı: uygulama yeniden açıldığında init_db çalışır.
        server.init_db()

        with server.db() as connection:
            row = connection.execute('select tx_type,tx_date from finance where id=?', (finance_id,)).fetchone()
        self.assertEqual(row['tx_type'], 'Gider')
        self.assertEqual(row['tx_date'], '2026-07-27')

    def test_fixed_income_categories_are_reconciled_without_touching_other(self):
        with server.db() as connection:
            sale_id = connection.execute(
                "insert into finance(tx_date,tx_type,category,amount,created_at) values('2026-09-05','Gider','Hayvan Satışı',65000,'2026-09-05T12:00:00')"
            ).lastrowid
            other_id = connection.execute(
                "insert into finance(tx_date,tx_type,category,amount,created_at) values('2026-09-05','Gelir','Diğer',10,'2026-09-05T12:00:00')"
            ).lastrowid
            server.reconcile_fixed_finance_types(connection)
            sale = connection.execute('select tx_type from finance where id=?', (sale_id,)).fetchone()
            other = connection.execute('select tx_type from finance where id=?', (other_id,)).fetchone()
        self.assertEqual(sale['tx_type'], 'Gelir')
        self.assertEqual(other['tx_type'], 'Gelir')

    def test_animal_finance_panel_uses_category_direction_even_before_restart(self):
        with server.db() as connection:
            animal_id = connection.execute(
                """insert into animals(
                       tag,gender,status,purchase_date,purchase_price,exit_date,daily_feed_cost,daily_care_cost
                   ) values('TRCH000002','Dişi','Satıldı','2026-07-27',45000,'2026-09-05',100,0)"""
            ).lastrowid
            connection.execute(
                """insert into finance(tx_date,tx_type,category,amount,description,payment_method,animal_id,created_at)
                   values('2026-07-27','Gelir','Hayvan Alımı',45000,'TRCH000002','Nakit',?,'2026-07-27T12:00:00')""",
                (animal_id,),
            )
            connection.execute(
                """insert into finance(tx_date,tx_type,category,amount,description,payment_method,animal_id,created_at)
                   values('2026-09-05','Gelir','Hayvan Satışı',65000,'TRCH000002','Nakit',?,'2026-09-05T12:00:00')""",
                (animal_id,),
            )

        session = 'hotfix122ch-panel'
        server.SESSIONS[session] = {'username': 'admin', 'role': 'admin'}
        http = server.QuietThreadingHTTPServer(('127.0.0.1', 0), server.App)
        threading.Thread(target=http.serve_forever, daemon=True).start()
        try:
            request = urllib.request.Request(
                f'http://127.0.0.1:{http.server_port}/animal?id={animal_id}',
                headers={'Cookie': f'sid={session}'},
            )
            with patch.object(server, 'license_status', return_value=(True, {}, '')):
                with urllib.request.urlopen(request, timeout=20) as response:
                    html = response.read().decode('utf-8')
        finally:
            http.shutdown()
            http.server_close()
            server.SESSIONS.pop(session, None)

        self.assertIn('Gelir<br><b>₺65.000,00</b>', html)
        self.assertIn('Gider<br><b>₺45.000,00</b>', html)
        self.assertIn('Maliyet<br><b>₺4.000,00</b>', html)
        self.assertIn('Net Kâr/Zarar<br><b>₺16.000,00</b>', html)
        self.assertIn('Net = gelir − gider − maliyet', html)
        self.assertIn('<td>Gider</td><td>Hayvan Alımı</td>', html)

    def test_version(self):
        self.assertEqual(server.APP_VERSION, '3.9.23 DEV4 Hotfix1.22ch')
        self.assertEqual(server.APP_LABEL, 'v3.9.23 DEV4 Hotfix1.22ch')


if __name__ == '__main__':
    unittest.main()
