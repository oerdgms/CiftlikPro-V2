import io
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from test_reports_import import server


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class _ScanResult:
    def __init__(self, text):
        self.text=text


class _FakeZxing:
    value='TR583074660'

    @classmethod
    def read_barcodes(cls, image):
        return [_ScanResult(cls.value)]


class Hotfix122BUTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.db_patch=patch.object(server,'DB',Path(self.temp.name)/'test.db')
        self.db_patch.start();server.init_db()
        with server.db() as c:
            c.execute("insert into animals(tag,nickname,gender,status) values('TR583074660','Sarı Boynuzlu','Dişi','Aktif')")
            c.execute("insert into calves(tag,nickname,gender,status,mother_id,birth_date) values('TR580000011','Yeni Buzağı','Dişi','Aktif',1,'2026-10-08')")
        server.SESSIONS['bu-test']={'username':'admin','role':'admin'}
        self.http=server.QuietThreadingHTTPServer(('127.0.0.1',0),server.App)
        threading.Thread(target=self.http.serve_forever,daemon=True).start()

    def tearDown(self):
        self.http.shutdown();self.http.server_close()
        server.SESSIONS.pop('bu-test',None)
        self.db_patch.stop();self.temp.cleanup()

    def post_scan(self):
        image=Image.new('RGB',(80,80),'white');payload=io.BytesIO();image.save(payload,format='PNG')
        boundary='----CiftlikProScanBoundary'
        body=(f'--{boundary}\r\nContent-Disposition: form-data; name="code_image"; filename="scan.png"\r\nContent-Type: image/png\r\n\r\n').encode()+payload.getvalue()+f'\r\n--{boundary}--\r\n'.encode()
        request=urllib.request.Request(
            f'http://127.0.0.1:{self.http.server_port}/animal-code-scan',data=body,method='POST',
            headers={'Cookie':'sid=bu-test','Content-Type':f'multipart/form-data; boundary={boundary}'},
        )
        opener=urllib.request.build_opener(_NoRedirect)
        with patch.object(server,'license_status',return_value=(True,{},'')),patch.object(server,'zxingcpp',_FakeZxing):
            try:opener.open(request,timeout=20)
            except urllib.error.HTTPError as exc:return exc.code,exc.headers.get('Location','')
        self.fail('Tarama POST isteği yönlendirme döndürmedi.')

    def test_code_helpers_accept_plain_url_and_digit_suffix(self):
        self.assertIn('TR583074660',server.scanned_animal_code_candidates('https://local/animal?tag=TR583074660'))
        target,_=server.find_animal_from_scanned_values(['3074660'])
        self.assertEqual(target,'/animal?id=1')

    def test_camera_scan_redirects_to_matching_animal(self):
        status,location=self.post_scan()
        self.assertEqual(status,303)
        self.assertTrue(location.startswith('/animal?id=1'))
        self.assertIn('msg=',location)

    def test_camera_scan_redirects_to_matching_calf(self):
        _FakeZxing.value='TR580000011'
        try:
            status,location=self.post_scan()
        finally:
            _FakeZxing.value='TR583074660'
        self.assertEqual(status,303)
        self.assertTrue(location.startswith('/calf?id=1'))

    def test_exe_build_files_include_decoder(self):
        root=Path(__file__).resolve().parents[1]
        self.assertIn('zxing-cpp', (root/'requirements.txt').read_text(encoding='utf-8'))
        self.assertIn('"zxingcpp"', (root/'CiftlikPro.spec').read_text(encoding='utf-8'))
        self.assertIn('zxing-cpp', (root/'.github/workflows/windows-installer.yml').read_text(encoding='utf-8'))
        self.assertEqual(server.APP_VERSION,'3.9.23 DEV4 Hotfix1.22bu')


if __name__=='__main__':
    unittest.main()
