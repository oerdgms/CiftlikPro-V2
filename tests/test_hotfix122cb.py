import tempfile
import threading
import unittest
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from unittest.mock import patch

from test_reports_import import server


class Hotfix122CBTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(server, 'DB', Path(self.temp.name) / 'test.db')
        self.db_patch.start()
        server.init_db()
        server.SESSIONS['cb-test'] = {'username': 'admin', 'role': 'admin'}
        self.http = server.QuietThreadingHTTPServer(('127.0.0.1', 0), server.App)
        threading.Thread(target=self.http.serve_forever, daemon=True).start()

    def tearDown(self):
        self.http.shutdown()
        self.http.server_close()
        server.SESSIONS.pop('cb-test', None)
        self.db_patch.stop()
        self.temp.cleanup()

    def get(self, path):
        request = urllib.request.Request(
            f'http://127.0.0.1:{self.http.server_port}{path}',
            headers={'Cookie': 'sid=cb-test'},
        )
        with patch.object(server, 'license_status', return_value=(True, {}, '')):
            with urllib.request.urlopen(request, timeout=20) as response:
                return response.read().decode('utf-8'), response.geturl()

    def post(self, path, data):
        request = urllib.request.Request(
            f'http://127.0.0.1:{self.http.server_port}{path}',
            data=urllib.parse.urlencode(data).encode('utf-8'),
            method='POST',
            headers={'Cookie': 'sid=cb-test', 'Content-Type': 'application/x-www-form-urlencoded'},
        )
        with patch.object(server, 'license_status', return_value=(True, {}, '')):
            with urllib.request.urlopen(request, timeout=20) as response:
                return response.read().decode('utf-8'), response.geturl()

    def add_case(self, tag='TR583074680', nickname='Sarı Boynuzlu'):
        today = date.today().isoformat()
        with server.db() as connection:
            animal_id = connection.execute(
                "insert into animals(tag,nickname,gender,status,paddock) values(?,?,'Dişi','Aktif','SA1')",
                (tag, nickname),
            ).lastrowid
            estrus_id = connection.execute(
                'insert into estrus_records(animal_id,estrus_date,signs,notes,created_at) values(?,?,?,?,?)',
                (animal_id, today, 'Huzursuzluk', 'Akşam gözlemi', today),
            ).lastrowid
        return animal_id, estrus_id

    def test_partial_tag_and_text_search_picker_is_available(self):
        self.add_case()
        html, _ = self.get('/estrus')
        self.assertIn('id="estrusAnimalSuggestions"', html)
        self.assertIn("normEstrus(a.tag).includes(q)", html)
        self.assertIn("if(hits.length===1)estrusId.value=String(hits[0].id)", html)
        self.assertIn('Küpe, takma ad, belirti veya not ara', html)
        self.assertIn('TR583074680', html)
        self.assertIn('Sarı Boynuzlu', html)
        self.assertIn('Huzursuzluk', html)
        self.assertIn('Akşam gözlemi', html)

    def test_existing_same_day_insemination_disables_duplicate_action(self):
        animal_id, _ = self.add_case()
        today = date.today().isoformat()
        with server.db() as connection:
            connection.execute(
                "insert into inseminations(animal_id,attempt,insemination_date,pregnancy_result,due_date) values(?,1,?,'Bekleniyor','')",
                (animal_id, today),
            )
        html, _ = self.get('/estrus')
        self.assertIn('Bugünkü Tohumlama Kayıtlı', html)
        self.assertIn(f'/inseminations?animal={animal_id}', html)
        self.assertNotIn(f'<input type="hidden" name="estrus_id" value="1"><button class="btn orange">🌱 Bugün Tohumlandı</button>', html)

    def test_duplicate_post_links_existing_record_and_closes_card(self):
        animal_id, estrus_id = self.add_case()
        today = date.today().isoformat()
        with server.db() as connection:
            insemination_id = connection.execute(
                "insert into inseminations(animal_id,attempt,insemination_date,pregnancy_result,due_date) values(?,1,?,'Bekleniyor','')",
                (animal_id, today),
            ).lastrowid
        html, url = self.post('/estrus-inseminate', {'estrus_id': estrus_id})
        self.assertIn('/estrus?', url)
        self.assertIn('kızgınlık kartı tamamlandı', html)
        with server.db() as connection:
            linked = connection.execute(
                'select insemination_id from estrus_decisions where estrus_id=?',
                (estrus_id,),
            ).fetchone()
        self.assertIsNotNone(linked)
        self.assertEqual(linked['insemination_id'], insemination_id)

    def test_version(self):
        self.assertEqual(server.APP_VERSION, '3.9.23 DEV4 Hotfix1.22cd')
        self.assertEqual(server.APP_LABEL, 'v3.9.23 DEV4 Hotfix1.22cd')


if __name__ == '__main__':
    unittest.main()
