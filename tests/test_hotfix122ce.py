import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

from test_reports_import import server


class Hotfix122CETests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(server, 'DB', Path(self.temp.name) / 'test.db')
        self.db_patch.start()
        server.init_db()

    def tearDown(self):
        self.db_patch.stop()
        self.temp.cleanup()

    def test_backdated_paddock_ration_accumulates_without_purchase_or_birth_date(self):
        today = date.today()
        start = today - timedelta(days=10)
        with server.db() as connection:
            feed_id = connection.execute(
                "insert into feed_catalog(name,category,active) values('CE Yem','Kesif Yemler',1)"
            ).lastrowid
            connection.execute(
                "insert into feed_prices(feed_id,effective_date,price_per_kg,notes) values(?,?,10,'test')",
                (feed_id, today.isoformat()),
            )
            ration_id = connection.execute(
                "insert into rations(name,target_group,notes,active,created_at) values('CE Rasyon','Test','',1,?)",
                (today.isoformat() + 'T00:00:00',),
            ).lastrowid
            connection.execute(
                "insert into ration_items(ration_id,feed_id,kg_per_head_day) values(?,?,2)",
                (ration_id, feed_id),
            )
            server.record_ration_item_history(connection, ration_id, feed_id, 2, today.isoformat(), 'test')
            paddock_id = connection.execute(
                """insert into paddocks(name,code,type,capacity,notes,active,created_at,updated_at)
                   values('CE Padok','CE','Besi',10,'',1,?,?)""",
                (today.isoformat() + 'T00:00:00', today.isoformat() + 'T00:00:00'),
            ).lastrowid
            connection.execute(
                "insert into paddock_rations(paddock_id,ration_id,start_date,active) values(?,?,?,1)",
                (paddock_id, ration_id, start.isoformat()),
            )
            animal_id = connection.execute(
                """insert into animals(tag,gender,status,paddock_id,purchase_price,purchase_date,birth_date,entry_date)
                   values('TRCE000001','Dişi','Aktif',?,0,'','','')""",
                (paddock_id,),
            ).lastrowid
            animal = connection.execute('select * from animals where id=?', (animal_id,)).fetchone()
            days, daily, accumulated, total = server.animal_cost_values(animal, connection)

        self.assertEqual(days, 10)
        self.assertAlmostEqual(daily, 20.0)
        self.assertAlmostEqual(accumulated, 200.0)
        self.assertAlmostEqual(total, 200.0)

    def test_entry_date_is_used_when_purchase_date_is_empty(self):
        entry = date.today() - timedelta(days=7)
        animal = {
            'id': -122,
            'purchase_price': 0,
            'daily_feed_cost': 12,
            'daily_care_cost': 3,
            'purchase_date': '',
            'entry_date': entry.isoformat(),
            'birth_date': '',
            'status': 'Aktif',
            'exit_date': '',
            'paddock_id': None,
        }
        days, daily, accumulated, total = server.animal_cost_values(animal)
        self.assertEqual(days, 7)
        self.assertAlmostEqual(daily, 15.0)
        self.assertAlmostEqual(accumulated, 105.0)
        self.assertAlmostEqual(total, 105.0)

    def test_version(self):
        self.assertEqual(server.APP_VERSION, '3.9.23 DEV4 Hotfix1.22ch')
        self.assertEqual(server.APP_LABEL, 'v3.9.23 DEV4 Hotfix1.22ch')


if __name__ == '__main__':
    unittest.main()
