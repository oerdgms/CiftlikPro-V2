import tempfile
import threading
import unittest
import urllib.parse
import urllib.request
from pathlib import Path
from unittest.mock import patch

from test_reports_import import server


class Hotfix122CCTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(server, 'DB', Path(self.temp.name) / 'test.db')
        self.db_patch.start()
        server.init_db()
        with server.db() as connection:
            self.animal_id = connection.execute(
                "insert into animals(tag,nickname,gender,status) values('TRCC0000001','Aralıklı Tedavi','Dişi','Aktif')"
            ).lastrowid
        server.SESSIONS['cc-test'] = {'username': 'admin', 'role': 'admin'}
        self.http = server.QuietThreadingHTTPServer(('127.0.0.1', 0), server.App)
        threading.Thread(target=self.http.serve_forever, daemon=True).start()

    def tearDown(self):
        self.http.shutdown()
        self.http.server_close()
        server.SESSIONS.pop('cc-test', None)
        self.db_patch.stop()
        self.temp.cleanup()

    def get(self, path):
        request = urllib.request.Request(
            f'http://127.0.0.1:{self.http.server_port}{path}',
            headers={'Cookie': 'sid=cc-test'},
        )
        with patch.object(server, 'license_status', return_value=(True, {}, '')):
            with urllib.request.urlopen(request, timeout=20) as response:
                return response.read().decode('utf-8')

    def post(self, path, data):
        request = urllib.request.Request(
            f'http://127.0.0.1:{self.http.server_port}{path}',
            data=urllib.parse.urlencode(data).encode('utf-8'),
            method='POST',
            headers={'Cookie': 'sid=cc-test', 'Content-Type': 'application/x-www-form-urlencoded'},
        )
        with patch.object(server, 'license_status', return_value=(True, {}, '')):
            with urllib.request.urlopen(request, timeout=20) as response:
                return response.read().decode('utf-8')

    def test_interval_schedule_creates_only_requested_application_days(self):
        slots = server.health_schedule_slots(
            'İlaç', '2026-10-09', treatment_days=2, times_per_day=1,
            treatment_interval_days=9,
        )
        self.assertEqual([slot['planned_date'] for slot in slots], ['2026-10-09', '2026-10-18'])
        self.assertEqual([slot['day_no'] for slot in slots], [1, 2])

        daily = server.health_schedule_slots('İlaç', '2026-10-09', treatment_days=3, times_per_day=1)
        self.assertEqual([slot['planned_date'] for slot in daily], ['2026-10-09', '2026-10-10', '2026-10-11'])

    def test_health_form_and_post_persist_x_days_interval(self):
        html = self.get('/health')
        self.assertIn('Kaç Uygulama Günü?', html)
        self.assertIn('Kaç Günde Bir?', html)
        self.assertIn('name="treatment_interval_days"', html)

        result = self.post('/health', {
            'scope_type': 'single',
            'subject_key': f'A:{self.animal_id}',
            'kind': 'İlaç',
            'product': 'GnRH',
            'applied_date': '2026-10-09',
            'treatment_days': '2',
            'treatment_interval_days': '9',
            'times_per_day': '1',
            'cost': '0',
            'notes': '9 günde bir uygulama',
        })
        self.assertIn('2 uygulama günü', result)
        self.assertIn('9 günde bir', result)
        with server.db() as connection:
            course = connection.execute(
                "select * from health_courses where product='GnRH' order by id desc limit 1"
            ).fetchone()
            tasks = connection.execute(
                'select planned_date from health_tasks where course_id=? order by day_no,application_no',
                (course['id'],),
            ).fetchall()
        self.assertEqual(course['treatment_interval_days'], 9)
        self.assertEqual([row['planned_date'] for row in tasks], ['2026-10-09', '2026-10-18'])

    def test_schema_and_version(self):
        with server.db() as connection:
            columns = {row[1] for row in connection.execute('pragma table_info(health_courses)').fetchall()}
        self.assertIn('treatment_interval_days', columns)
        self.assertEqual(server.APP_VERSION, '3.9.23 DEV4 Hotfix1.22cd')
        self.assertEqual(server.APP_LABEL, 'v3.9.23 DEV4 Hotfix1.22cd')


if __name__ == '__main__':
    unittest.main()
