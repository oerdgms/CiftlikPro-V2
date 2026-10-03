import base64
import pathlib
import sys
import tempfile
import threading
import unittest
import urllib.request
import uuid
from unittest.mock import patch


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'app'))
import server


PNG_1X1 = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII='
)


def multipart(fields, file_field, filename, content, content_type='image/png'):
    boundary = '----CiftlikProTest' + uuid.uuid4().hex
    chunks = []
    for name, value in fields.items():
        chunks.extend([
            f'--{boundary}\r\n'.encode(),
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(),
            str(value).encode('utf-8'), b'\r\n'
        ])
    chunks.extend([
        f'--{boundary}\r\n'.encode(),
        f'Content-Disposition: form-data; name="{file_field}"; filename="{filename}"\r\n'.encode(),
        f'Content-Type: {content_type}\r\n\r\n'.encode(),
        content, b'\r\n', f'--{boundary}--\r\n'.encode()
    ])
    return b''.join(chunks), boundary


class PromotedAnimalEditTests(unittest.TestCase):
    def test_photo_update_allows_the_linked_promoted_calf_tag(self):
        server.init_db()
        suffix = uuid.uuid4().hex[:10].upper()
        tag = 'TR' + suffix
        other_tag = 'TRX' + suffix
        with server.db() as con:
            aid = con.execute(
                "insert into animals(tag,nickname,gender,birth_date,status) values(?,'','Dişi','2025-11-05','Aktif')",
                (tag,)
            ).lastrowid
            cid = con.execute(
                "insert into calves(tag,mother_id,birth_date,gender,status,promoted_animal_id) values(?,0,'2025-11-05','Dişi','Aktif',?)",
                (tag, aid)
            ).lastrowid
            other_id = con.execute(
                "insert into animals(tag,nickname,gender,birth_date,status) values(?,'','Dişi','2025-01-01','Aktif')",
                (other_tag,)
            ).lastrowid
            self.assertFalse(server.animal_edit_tag_conflict(con, tag.lower(), aid))
            self.assertTrue(server.animal_edit_tag_conflict(con, other_tag, aid))

        server.SESSIONS['promoted-edit-test'] = {'username': 'admin', 'role': 'admin'}
        http = server.QuietThreadingHTTPServer(('127.0.0.1', 0), server.App)
        threading.Thread(target=http.serve_forever, daemon=True).start()
        try:
            fields = {
                'id': aid, 'tag': tag, 'nickname': 'Fotoğraflı', 'gender': 'Dişi',
                'breed': 'Simental', 'birth_date': '2025-11-05', 'paddock': 'SO8',
                'photo_url': '', 'status': 'Aktif', 'sold_price': '0',
                'purchase_date': '', 'purchase_price': '0', 'purchase_weight': '0',
                'daily_feed_cost': '0', 'daily_care_cost': '0',
                'target_sale_price': '0', 'notes': ''
            }
            data, boundary = multipart(fields, 'photo_file', 'hayvan.png', PNG_1X1)
            request = urllib.request.Request(
                f'http://127.0.0.1:{http.server_port}/animal-edit', data=data,
                headers={
                    'Cookie': 'sid=promoted-edit-test',
                    'Content-Type': f'multipart/form-data; boundary={boundary}'
                }, method='POST'
            )
            with tempfile.TemporaryDirectory() as tmp, \
                 patch.object(server, 'UPLOADS', pathlib.Path(tmp)), \
                 patch.object(server, 'license_status', return_value=(True, {}, '')):
                with urllib.request.urlopen(request, timeout=20) as response:
                    html = response.read().decode('utf-8')
                self.assertIn('Hayvan başarıyla güncellendi.', html)
                with server.db() as con:
                    animal = con.execute('select nickname,photo_url from animals where id=?', (aid,)).fetchone()
                    calf = con.execute('select tag from calves where id=?', (cid,)).fetchone()
                self.assertEqual(animal['nickname'], 'Fotoğraflı')
                self.assertTrue(animal['photo_url'].startswith('/uploads/animal_edit_'))
                self.assertTrue((pathlib.Path(tmp) / pathlib.Path(animal['photo_url']).name).is_file())
                self.assertEqual(calf['tag'], tag)
        finally:
            http.shutdown(); http.server_close()
            server.SESSIONS.pop('promoted-edit-test', None)
            with server.db() as con:
                con.execute('delete from calves where id=?', (cid,))
                con.execute('delete from animals where id in (?,?)', (aid, other_id))


if __name__ == '__main__':
    unittest.main()
