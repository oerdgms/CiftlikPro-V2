import tempfile
import threading
import unittest
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from unittest.mock import patch

from test_reports_import import server


class Hotfix122CDTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(server, 'DB', Path(self.temp.name) / 'test.db')
        self.db_patch.start()
        server.init_db()
        today = date.today().isoformat()
        with server.db() as connection:
            self.animal_ids = [
                connection.execute(
                    "insert into animals(tag,nickname,gender,status) values(?,?,'Dişi','Aktif')",
                    (tag, nickname),
                ).lastrowid
                for tag, nickname in (
                    ('TR583074655', 'Boynu Şiş'),
                    ('TR583074668', 'Boynuzlu Beyaz'),
                )
            ]
            self.course_id = connection.execute(
                """insert into health_courses(
                    kind,product,scope_type,start_date,treatment_days,
                    treatment_interval_days,times_per_day,created_at
                ) values('İlaç','GnRH','multi',?,1,1,1,?)""",
                (today, today),
            ).lastrowid
            for animal_id in self.animal_ids:
                connection.execute(
                    """insert into health_tasks(
                        course_id,animal_id,planned_date,day_no,day_total,
                        application_no,applications_per_day,status
                    ) values(?,?,?,1,1,1,1,'Bekliyor')""",
                    (self.course_id, animal_id, today),
                )
        server.SESSIONS['cd-test'] = {'username': 'admin', 'role': 'admin'}
        self.http = server.QuietThreadingHTTPServer(('127.0.0.1', 0), server.App)
        threading.Thread(target=self.http.serve_forever, daemon=True).start()

    def tearDown(self):
        self.http.shutdown()
        self.http.server_close()
        server.SESSIONS.pop('cd-test', None)
        self.db_patch.stop()
        self.temp.cleanup()

    def get(self, path):
        request = urllib.request.Request(
            f'http://127.0.0.1:{self.http.server_port}{path}',
            headers={'Cookie': 'sid=cd-test'},
        )
        with patch.object(server, 'license_status', return_value=(True, {}, '')):
            with urllib.request.urlopen(request, timeout=20) as response:
                return response.read().decode('utf-8')

    def test_multi_plan_is_one_dashboard_job_with_all_targets(self):
        with server.db() as connection:
            entries = [
                row for row in server.health_plan_entries(connection, horizon_days=30)
                if row['source'] == 'course'
            ]
        self.assertEqual(len(entries), 1)
        entry = entries[0]
        self.assertEqual(entry['subject'], 'Çoklu Hayvan Planı')
        self.assertEqual(entry['course_id'], self.course_id)
        self.assertEqual(entry['target_count'], 2)
        self.assertIn('TR583074655', entry['target_tags'])
        self.assertIn('TR583074668', entry['target_tags'])

        dashboard = self.get('/')
        self.assertIn('İlaç · Çoklu Hayvan Planı', dashboard)
        self.assertIn('2 hayvan · TR583074655, TR583074668', dashboard)
        expected_ref = f'{self.course_id}:{date.today().isoformat()}:1:1:1'
        encoded_ref = urllib.parse.quote(expected_ref, safe='')
        self.assertIn(
            f'/health?filter=today&amp;plan={self.course_id}&amp;task={encoded_ref}',
            dashboard,
        )
        self.assertNotIn('/health?filter=today&amp;search=TR583074655', dashboard)

    def test_dashboard_link_opens_exact_grouped_health_card(self):
        plan_ref = f'{self.course_id}:{date.today().isoformat()}:1:1:1'
        query = urllib.parse.urlencode({
            'filter': 'today', 'plan': self.course_id, 'task': plan_ref,
        })
        health = self.get('/health?' + query)
        self.assertIn(f'data-health-course="{self.course_id}"', health)
        self.assertIn(f'data-health-plan-ref="{plan_ref}"', health)
        self.assertIn('👥 Çoklu Hayvan Planı', health)
        self.assertIn('🐄 TR583074655, TR583074668', health)
        self.assertIn('id="hotfix122cd-health-plan-focus"', health)
        self.assertIn("card.dataset.healthPlanRef===requestedTask", health)

    def test_version(self):
        self.assertEqual(server.APP_VERSION, '3.9.23 DEV4 Hotfix1.22cd')
        self.assertEqual(server.APP_LABEL, 'v3.9.23 DEV4 Hotfix1.22cd')


if __name__ == '__main__':
    unittest.main()
