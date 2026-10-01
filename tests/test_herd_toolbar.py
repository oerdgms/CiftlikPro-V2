import threading
import unittest
import urllib.request
from unittest.mock import patch
from test_reports_import import server


class HerdToolbarTests(unittest.TestCase):
    def test_filter_form_keeps_category_and_paddock(self):
        server.init_db()
        with server.db() as c:
            aid=c.execute("insert into animals(tag,nickname,gender,breed,paddock,birth_date,status,photo_url) values('TRHERDAM','Boncuk','Dişi','Simental','AM01','2024-01-02','Aktif','/uploads/herd-test.webp')").lastrowid
        server.SESSIONS['herd-am']={'username':'admin','role':'admin'}
        http=server.QuietThreadingHTTPServer(('127.0.0.1',0),server.App)
        threading.Thread(target=http.serve_forever,daemon=True).start()
        try:
            with patch.object(server,'license_status',return_value=(True,{},'')):
                req=urllib.request.Request(f'http://127.0.0.1:{http.server_port}/all-animals?kind=female&paddock=AM01&q=TRHERDAM&sort=age&dir=desc',headers={'Cookie':'sid=herd-am'})
                with urllib.request.urlopen(req,timeout=20) as response:html=response.read().decode()
            self.assertIn('class="card herd-filter"',html)
            self.assertIn('type="hidden" name="kind" value="female"',html)
            self.assertNotIn('<select name="kind">',html)
            self.assertIn('class="herd-filter-details" open',html)
            self.assertIn('1 hayvan · AM01 · TRHERDAM',html)
            self.assertIn('name="sort" value="age"',html)
            self.assertIn('class="herd-sort active"',html)
            self.assertIn('sort=age',html)
            self.assertIn('class="herd-photo"',html)
            self.assertIn('src="/uploads/herd-test.webp"',html)
            self.assertIn('class="herd-animal-summary"',html)
            self.assertIn('Boncuk',html)
            self.assertIn('return confirm(',html)
            self.assertIn('class="hf122am-herd"',html)
            self.assertLess(html.index('hotfix122am-herd-toolbar'),html.index('</head>'))
            self.assertLess(html.index('hotfix122an-herd-list'),html.index('</head>'))
        finally:
            http.shutdown();http.server_close();server.SESSIONS.pop('herd-am',None)
            with server.db() as c:c.execute('delete from animals where id=?',(aid,))

    def test_toolbar_is_not_in_other_modules(self):
        self.assertNotIn('hotfix122am-herd-toolbar',server.page('Sağlık','İçerik','/health'))
        self.assertNotIn('hotfix122an-herd-list',server.page('Sağlık','İçerik','/health'))

    def test_age_sort_is_server_side_and_missing_photo_has_fallback(self):
        server.init_db()
        with server.db() as c:
            older=c.execute("insert into animals(tag,gender,birth_date,status) values('TRSORT-OLDER','Erkek','2020-01-01','Aktif')").lastrowid
            younger=c.execute("insert into animals(tag,gender,birth_date,status) values('TRSORT-YOUNGER','Erkek','2024-01-01','Aktif')").lastrowid
        server.SESSIONS['herd-sort']={'username':'admin','role':'admin'}
        http=server.QuietThreadingHTTPServer(('127.0.0.1',0),server.App)
        threading.Thread(target=http.serve_forever,daemon=True).start()
        try:
            with patch.object(server,'license_status',return_value=(True,{},'')):
                req=urllib.request.Request(f'http://127.0.0.1:{http.server_port}/all-animals?q=TRSORT&sort=age&dir=desc',headers={'Cookie':'sid=herd-sort'})
                with urllib.request.urlopen(req,timeout=20) as response:html=response.read().decode()
            self.assertLess(html.index('TRSORT-OLDER'),html.index('TRSORT-YOUNGER'))
            self.assertIn('<span aria-hidden="true">🐂</span>',html)
        finally:
            http.shutdown();http.server_close();server.SESSIONS.pop('herd-sort',None)
            with server.db() as c:c.execute('delete from animals where id in (?,?)',(older,younger))


if __name__=='__main__':unittest.main()
