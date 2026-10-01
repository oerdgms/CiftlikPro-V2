import threading
import unittest
import urllib.request
from datetime import date, timedelta
from unittest.mock import patch

from test_reports_import import server


class ReproductionMobileTests(unittest.TestCase):
    def test_mobile_accordion_photo_limit_and_actions_are_rendered(self):
        server.init_db()
        animal_ids = []
        insemination_ids = []
        insem_date = (date.today() - timedelta(days=30)).isoformat()
        with server.db() as c:
            for index in range(4):
                photo = '/uploads/repro-test.webp' if index == 0 else ''
                animal_id = c.execute(
                    "insert into animals(tag,nickname,gender,breed,paddock,status,photo_url) values(?,?,?,?,?,'Aktif',?)",
                    (f'TRREPRO{index}', f'Deneme {index}', 'Dişi', 'Simental', 'RP01', photo),
                ).lastrowid
                animal_ids.append(animal_id)
                insemination_ids.append(c.execute(
                    "insert into inseminations(animal_id,insemination_date,attempt,pregnancy_result) values(?,?,1,'Bekleniyor')",
                    (animal_id, insem_date),
                ).lastrowid)
        server.SESSIONS['repro-mobile'] = {'username': 'admin', 'role': 'admin'}
        http = server.QuietThreadingHTTPServer(('127.0.0.1', 0), server.App)
        threading.Thread(target=http.serve_forever, daemon=True).start()
        try:
            with patch.object(server, 'license_status', return_value=(True, {}, '')):
                request = urllib.request.Request(
                    f'http://127.0.0.1:{http.server_port}/reproduction-center',
                    headers={'Cookie': 'sid=repro-mobile'},
                )
                with urllib.request.urlopen(request, timeout=20) as response:
                    html = response.read().decode()
            self.assertIn('hotfix122ao-reproduction-center', html)
            self.assertIn('hotfix122ap-reproduction-center', html)
            self.assertIn('hotfix122aq-reproduction-detail', html)
            self.assertIn('class="v117-board repro-board-compact"', html)
            self.assertIn('data-repro-section="control"', html)
            self.assertIn('data-mobile-open="1"', html)
            self.assertIn('Tümünü Gör (4)', html)
            self.assertIn('src="/uploads/repro-test.webp"', html)
            self.assertIn('class="repro-photo"', html)
            self.assertIn('Kontrol Kaydet', html)
            self.assertIn("index>=3", html)
            self.assertIn("matches.length", html)
            self.assertIn("nowMobile!==wasMobile", html)
            self.assertNotIn("window.addEventListener('resize',()=>{applyAccordion();run()", html)
            self.assertIn('class="repro-stage-tabs"', html)
            self.assertIn('data-repro-filter="pregnant"', html)
            self.assertIn('white-space:nowrap!important', html)
            self.assertIn('class="quick-metrics repro-selected-metrics"', html)
            self.assertIn('class="pill repro-tag-metric"', html)
            self.assertIn('class="repro-link-mobile">Kartı Aç', html)
            self.assertIn('grid-template-columns:repeat(5,minmax(0,1fr))', html)
            self.assertIn('.repro-selected-metrics .repro-tag-metric{display:none!important}', html)
            self.assertLess(html.index('hotfix122ao-reproduction-center'), html.index('</head>'))
            self.assertLess(html.index('hotfix122ap-reproduction-center'), html.index('</head>'))
            self.assertLess(html.index('hotfix122aq-reproduction-detail'), html.index('</head>'))
        finally:
            http.shutdown()
            http.server_close()
            server.SESSIONS.pop('repro-mobile', None)
            with server.db() as c:
                c.execute(
                    'delete from inseminations where id in (%s)' % ','.join('?' * len(insemination_ids)),
                    insemination_ids,
                )
                c.execute(
                    'delete from animals where id in (%s)' % ','.join('?' * len(animal_ids)),
                    animal_ids,
                )

    def test_reproduction_css_is_scoped_to_reproduction_center(self):
        self.assertNotIn('hotfix122ao-reproduction-center', server.page('Sağlık', 'İçerik', '/health'))
        self.assertNotIn('hotfix122ap-reproduction-center', server.page('Sağlık', 'İçerik', '/health'))
        self.assertNotIn('hotfix122aq-reproduction-detail', server.page('Sağlık', 'İçerik', '/health'))


if __name__ == '__main__':
    unittest.main()
