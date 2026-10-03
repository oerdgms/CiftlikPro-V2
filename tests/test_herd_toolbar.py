import threading
import unittest
import urllib.parse
import urllib.request
from unittest.mock import patch
from test_reports_import import server


class HerdToolbarTests(unittest.TestCase):
    def test_legacy_category_routes_open_the_filtered_herd_center(self):
        server.init_db()
        server.SESSIONS['herd-routes']={'username':'admin','role':'admin'}
        http=server.QuietThreadingHTTPServer(('127.0.0.1',0),server.App)
        threading.Thread(target=http.serve_forever,daemon=True).start()
        try:
            with patch.object(server,'license_status',return_value=(True,{},'')):
                for old_path,kind in (('/animals','female'),('/males','male'),('/calves','calf')):
                    with self.subTest(old_path=old_path):
                        req=urllib.request.Request(
                            f'http://127.0.0.1:{http.server_port}{old_path}?q=ROUTE-CHECK',
                            headers={'Cookie':'sid=herd-routes'}
                        )
                        with urllib.request.urlopen(req,timeout=20) as response:
                            html=response.read().decode()
                            final_url=response.geturl()
                        self.assertIn('/all-animals?',final_url)
                        self.assertIn(f'kind={kind}',final_url)
                        self.assertIn('q=ROUTE-CHECK',final_url)
                        self.assertIn('🐄 Sürü Merkezi',html)
                        self.assertIn(f'name="kind" value="{kind}"',html)
            nav_html=server.page('Test','İçerik','/all-animals','admin')
            self.assertIn('href="/all-animals?kind=female"',nav_html)
            self.assertIn('href="/all-animals?kind=male"',nav_html)
            self.assertIn('href="/all-animals?kind=calf"',nav_html)
        finally:
            http.shutdown();http.server_close();server.SESSIONS.pop('herd-routes',None)

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
        self.assertNotIn('hotfix122as-herd-view',server.page('Sağlık','İçerik','/health'))
        self.assertNotIn('hotfix122at-mobile-herd-views',server.page('Sağlık','İçerik','/health'))

    def test_mobile_view_fix_is_last_and_scoped_to_herd_center(self):
        html=server.page('Sürü Merkezi','İçerik','/all-animals','admin')
        self.assertIn('id="hotfix122at-mobile-herd-views"',html)
        self.assertLess(html.index('hotfix122as-herd-view'),html.index('hotfix122at-mobile-herd-views'))
        self.assertLess(html.index('hotfix122at-mobile-herd-views'),html.index('</head>'))
        self.assertIn('grid-template-columns:minmax(0,1fr) 116px!important',html)
        self.assertIn(".btn:after{content:none!important",html)
        self.assertIn('grid-template-columns:58px minmax(0,1fr)!important',html)

    def test_desktop_filter_controls_share_one_alignment_grid(self):
        html=server.page('Sürü Merkezi','İçerik','/all-animals','admin')
        self.assertIn('id="hotfix122av-herd-filter-alignment"',html)
        self.assertLess(html.index('hotfix122at-mobile-herd-views'),html.index('hotfix122av-herd-filter-alignment'))
        self.assertIn('grid-template-rows:16px 44px!important',html)
        self.assertIn('grid-template-columns:minmax(140px,1fr) 112px auto!important',html)
        self.assertIn('margin:21px 0 0!important;height:44px!important',html)
        self.assertNotIn('hotfix122av-herd-filter-alignment',server.page('Sağlık','İçerik','/health'))

    def test_view_switch_is_saved_per_user_and_rendered_without_flash(self):
        server.init_db()
        with server.db() as c:c.execute("delete from settings where setting_key='herd_view_herd-view'")
        server.SESSIONS['herd-view']={'username':'herd-view','role':'admin'}
        http=server.QuietThreadingHTTPServer(('127.0.0.1',0),server.App)
        threading.Thread(target=http.serve_forever,daemon=True).start()
        try:
            with patch.object(server,'license_status',return_value=(True,{},'')):
                request=urllib.request.Request(
                    f'http://127.0.0.1:{http.server_port}/herd-view',
                    data=urllib.parse.urlencode({'view':'cards'}).encode(),
                    headers={'Cookie':'sid=herd-view','Content-Type':'application/x-www-form-urlencoded'},
                    method='POST'
                )
                with urllib.request.urlopen(request,timeout=20) as response:self.assertEqual(response.status,204)
                request=urllib.request.Request(f'http://127.0.0.1:{http.server_port}/all-animals?kind=calf',headers={'Cookie':'sid=herd-view'})
                with urllib.request.urlopen(request,timeout=20) as response:html=response.read().decode()
            self.assertIn('data-herd-view="cards"',html)
            self.assertIn('data-herd-view-button="details"',html)
            self.assertIn('data-herd-view-button="cards" aria-pressed="true"',html)
            self.assertIn('data-herd-view-button="compact"',html)
            self.assertIn('id="hotfix122as-herd-view"',html)
            self.assertIn("fetch('/herd-view'",html)
            with server.db() as c:
                saved=c.execute("select setting_value from settings where setting_key='herd_view_herd-view'").fetchone()
            self.assertEqual(saved['setting_value'],'cards')
        finally:
            http.shutdown();http.server_close();server.SESSIONS.pop('herd-view',None)
            with server.db() as c:c.execute("delete from settings where setting_key='herd_view_herd-view'")

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
