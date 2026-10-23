"""Desktop and mobile must expose the same explicit dairy state and settings."""
import json
import tempfile
import threading
import unittest
import urllib.request
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlencode

from test_reports_import import server
import dairy_management as dairy
import desktop_views as wide
import home_layout
import mobile_reference as ref
import mobile_ui


class InterfaceParityTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.patch=patch.object(server,'DB',Path(self.temp.name)/'parity.db');self.patch.start()
        server.init_db();self.today=server.date.today().isoformat();self.ids=[]
        with server.db() as c:
            for i in range(14):
                self.ids.append(c.execute("insert into animals(tag,nickname,gender,status,birth_date,paddock) values(?,?,'Dişi','Aktif','2020-01-01','PARITY-PAD')",('PARITY-'+str(i).zfill(2),'İnci '+str(i))).lastrowid)
            self.male=c.execute("insert into animals(tag,gender,status) values('PARITY-MALE','Erkek','Aktif')").lastrowid
            self.calf=c.execute("insert into calves(tag,mother_id,birth_date,gender,status) values('PARITY-CALF',?,?,'Erkek','Aktif')",(self.ids[0],self.today)).lastrowid
            c.execute('insert into milk(animal_id,measure_date,liters,morning_liters,evening_liters) values(?,?,?,?,?)',(self.ids[0],self.today,25,12,13))
        with server.db() as c:dairy.save_status(c,self.ids[:12],'lactating',self.today)

    def tearDown(self):
        self.patch.stop();self.temp.cleanup()

    def test_desktop_and_mobile_summary_use_the_same_manual_membership(self):
        desktop=wide.summary(vars(server),'admin')
        mobile=ref.home(vars(server),'admin',mobile_ui.icon,mobile_ui.task_url)
        self.assertIn('<span>Sağmal</span><b>12</b>',desktop)
        self.assertIn('<small>Sağmal</small><b>12</b>',mobile)
        self.assertIn('<span>Erkek</span><b>1</b>',desktop)
        self.assertIn('/dairy-status',desktop)

    def test_desktop_filter_is_global_before_pagination(self):
        view=ref.herd_selection(vars(server),'/all-animals?group=lactating&per_page=10&page=2')
        self.assertEqual(len(view['selected']),12)
        desktop=wide.herd_markup(vars(server),'/all-animals?group=lactating&per_page=10&page=2')
        self.assertIn('<b role="status">12 hayvan</b>',desktop)
        self.assertIn('PARITY-10',desktop)
        self.assertIn('PARITY-11',desktop)
        self.assertNotIn('PARITY-00',desktop)
        self.assertNotIn('PARITY-12',desktop)
        self.assertIn('group=lactating',desktop)

    def test_desktop_combines_status_kind_paddock_and_turkish_search(self):
        desktop=wide.herd_markup(vars(server),'/all-animals?group=lactating&kind=female&paddock=PARITY-PAD&q=%C4%B0NC%C4%B0+11')
        self.assertIn('<b role="status">1 hayvan</b>',desktop)
        self.assertIn('PARITY-11',desktop)
        self.assertNotIn('PARITY-10',desktop)
        self.assertIn('name="group"',desktop)

    def test_module_directory_exposes_thirteen_tiles_with_a_unified_health_hub(self):
        text=wide.modules_markup(mobile_ui.icon)
        self.assertEqual(text.count('class="cp-module-tile"'),13)
        for url in ('/milk-center','/health','/agriculture','/archive/sold','/backups'):
            self.assertIn('href="'+url+'"',text)
        self.assertNotIn('<details',text)
        self.assertNotIn('Diğer Modüller',text)
        self.assertNotIn('href="/synchronization"',text)
        self.assertNotIn('href="/medicines"',text)

    def test_milk_center_only_calls_explicit_members_sağmal(self):
        text=wide.milk_markup(vars(server),'/milk-center')
        self.assertIn('data-milk-lactating>12<',text)
        self.assertIn('12 hayvan</b>',text)
        self.assertNotIn('PARITY-12',text)
        self.assertIn('name="morning_'+str(self.ids[0])+'" value="12.0"',text)
        self.assertIn('action="/milk-center"',text)
        all_text=wide.milk_markup(vars(server),'/milk-center?group=all')
        self.assertIn('14 hayvan</b>',all_text)
        self.assertIn('PARITY-12',all_text)

    def test_unknown_start_has_no_birth_derived_dim_or_projection(self):
        with server.db() as c:
            c.execute('insert into calves(tag,mother_id,birth_date,gender) values(?,?,?,?)',('PARITY-BIRTH',self.ids[0],(server.date.today()-timedelta(days=80)).isoformat(),'Dişi'))
            animal=c.execute('select * from animals where id=?',(self.ids[0],)).fetchone()
            sm=wide.milk_summary(c,animal)
        self.assertIsNone(sm['state']['dim'])
        self.assertIsNone(sm['total'])
        self.assertIsNone(sm['projected305'])
        document="<html><main><div class='quick-metrics'><span>Laktasyon Günü<br><b>81 DIM</b></span></div></main></html>"
        text=wide.animal_document(vars(server),document,self.ids[0])
        self.assertNotIn('81 DIM',text)
        self.assertIn('Laktasyon Durumu',text)

    def test_manual_start_limits_lactation_total_but_keeps_actual_daily_entries(self):
        start=(server.date.today()-timedelta(days=10)).isoformat()
        with server.db() as c:
            c.execute('insert into milk(animal_id,measure_date,liters) values(?,?,?)',(self.ids[0],(server.date.today()-timedelta(days=20)).isoformat(),100))
        with server.db() as c:dairy.save_status(c,[self.ids[0]],'lactating',self.today,start,'2')
        with server.db() as c:
            animal=c.execute('select * from animals where id=?',(self.ids[0],)).fetchone()
            sm=wide.milk_summary(c,animal)
        self.assertEqual(sm['state']['dim'],10)
        self.assertEqual(sm['total'],25)
        self.assertEqual(sm['today'],25)

    def test_layout_defaults_are_fresh_and_invalid_saved_data_falls_back(self):
        config=home_layout.load(vars(server),'admin');config['cards'].clear()
        self.assertEqual(len(home_layout.load(vars(server),'admin')['cards']),6)
        with server.db() as c:c.execute('insert into settings(setting_key,setting_value) values(?,?)',('reference_home_broken','not json'))
        self.assertEqual(home_layout.load(vars(server),'broken'),home_layout.defaults())

    def test_layout_order_visibility_and_count_persist_per_user(self):
        config={'sections':['tasks','summary'],'cards':['male','lactating','all'],'task_limit':5}
        home_layout.save(vars(server),'admin',config)
        self.assertEqual(home_layout.load(vars(server),'admin'),config)
        self.assertEqual(home_layout.load(vars(server),'another'),home_layout.defaults())
        mobile=ref.home(vars(server),'admin',mobile_ui.icon,mobile_ui.task_url)
        desktop=wide.summary(vars(server),'admin')
        self.assertIn('data-task-limit="5"',mobile)
        self.assertIn('data-cp-home-section="business" hidden',mobile)
        self.assertLess(mobile.index('data-cp-home-section="tasks"'),mobile.index('data-cp-home-section="summary"'))
        self.assertLess(mobile.index('<small>Erkek</small>'),mobile.index('<small>Sağmal</small>'))
        self.assertLess(desktop.index('<span>Erkek</span>'),desktop.index('<span>Sağmal</span>'))
        self.assertNotIn('<small>Kuru</small>',mobile)
        self.assertNotIn('<span>Kuru</span>',desktop)

    def test_invalid_layout_never_overwrites_saved_preferences(self):
        good=home_layout.defaults();home_layout.save(vars(server),'admin',good)
        for change in ({'cards':[]},{'sections':[]},{'cards':['male','male']},{'sections':['bad']},{'task_limit':100},{'task_limit':True}):
            with self.subTest(change=change):
                with self.assertRaises(ValueError):home_layout.save(vars(server),'admin',good|change)
                self.assertEqual(home_layout.load(vars(server),'admin'),good)

    def test_settings_keep_legacy_desktop_editor_separate_from_new_home_editor(self):
        text=home_layout.editor(vars(server),'admin')
        self.assertIn('action="/home-layout/save"',text)
        self.assertIn('href="/?edit=1&amp;desktop_editor=1"',text)
        self.assertIn('name="action" value="reset"',text)

    def test_settings_user_content_is_escaped(self):
        with server.db() as c:c.execute('update animals set nickname=? where id=?',('<img src=x onerror=alert(1)>',self.ids[0]))
        text=wide.herd_markup(vars(server),'/all-animals?group=lactating')
        self.assertIn('&lt;img src=x onerror=alert(1)&gt;',text)
        self.assertNotIn('<img src=x',text)

    def test_http_routes_share_features_and_settings_save_reset(self):
        http=server.QuietThreadingHTTPServer(('127.0.0.1',0),server.App)
        threading.Thread(target=http.serve_forever,daemon=True).start()
        server.SESSIONS['parity-test']={'username':'admin','role':'admin'}
        base='http://127.0.0.1:'+str(http.server_port)
        def request(path,data=None,login=True):
            req=urllib.request.Request(base+path,data=data,headers={'Cookie':'sid=parity-test'} if login else {})
            with urllib.request.urlopen(req,timeout=20) as response:return response.read().decode(),response.url
        try:
            with patch.object(server,'license_status',return_value=(True,{},'')):
                for path in ('/modules','/?app_view=modules'):
                    text,_=request(path);self.assertEqual(text.count('class="cp-module-tile"'),13)
                text,_=request('/milk-center');self.assertIn('data-milk-lactating>12<',text)
                text,_=request('/all-animals?group=lactating');self.assertIn('class="cp-wide-herd cp-wide-only"',text)
                text,_=request('/animal?id='+str(self.ids[0]));self.assertIn('cp-wide-dairy',text)
                text,_=request('/farm-profile');self.assertIn('href="/home-layout"',text);self.assertNotIn('href="/?edit=1"><b>▦ Dashboard',text)
                _,url=request('/home-layout',login=False);self.assertIn('/login',url)
                data=urlencode([('sections','summary'),('cards','male'),('cards','lactating'),('task_limit','5'),('action','save')]).encode()
                request('/home-layout/save',data)
                self.assertEqual(home_layout.load(vars(server),'admin')['cards'],['male','lactating'])
                request('/home-layout/reset',b'action=reset')
                self.assertEqual(home_layout.load(vars(server),'admin'),home_layout.defaults())
        finally:
            http.shutdown();http.server_close();server.SESSIONS.pop('parity-test',None)


if __name__=='__main__':unittest.main()
