"""Record-backed reference UI contracts; no fixture is shipped in the runtime DB."""
import json
import tempfile
import threading
import unittest
import urllib.request
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

from test_reports_import import server
import mobile_reference as ref
import mobile_ui
import dairy_management as dairy


class ReferenceMobileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(server,'DB',Path(self.temp.name)/'reference.db')
        self.db_patch.start()
        server.init_db()
        self.today = server.date.today()
        self.icon = mobile_ui.icon
        with server.db() as c:
            stamp = server.datetime.now().isoformat()
            self.pad = c.execute('insert into paddocks(name,capacity,created_at) values(?,?,?)',('Sağmal & Düve',50,stamp)).lastrowid
            self.milking = c.execute("insert into animals(tag,nickname,gender,status,birth_date,paddock_id,paddock,purchase_price) values('TR580000000001','İnci','Dişi','Aktif','2020-01-01',?,'Sağmal & Düve',45000)",(self.pad,)).lastrowid
            self.dry = c.execute("insert into animals(tag,gender,status,birth_date,dry_since) values('TR580000000002','Dişi','Aktif','2021-01-01',?)",((self.today-timedelta(days=10)).isoformat(),)).lastrowid
            self.heifer = c.execute("insert into animals(tag,gender,status,birth_date) values('TR580000000003','Dişi','Aktif','2025-01-01')").lastrowid
            self.male = c.execute("insert into animals(tag,gender,status,birth_date) values('TR580000000004','Erkek','Aktif','2024-01-01')").lastrowid
            self.calf = c.execute("insert into calves(tag,mother_id,gender,status,birth_date) values('TR580000000005',?,'Dişi','Aktif',?)",(self.milking,(self.today-timedelta(days=80)).isoformat())).lastrowid
            c.execute('insert into milk(animal_id,measure_date,liters) values(?,?,?)',(self.milking,self.today.isoformat(),28.5))
        with server.db() as c:dairy.save_status(c,[self.milking],'lactating',self.today.isoformat())
        with server.db() as c:dairy.save_status(c,[self.heifer],'heifer',self.today.isoformat())

    def tearDown(self):
        self.db_patch.stop()
        self.temp.cleanup()

    def records(self):
        with server.db() as c:return ref.herd_records(vars(server),c)

    def test_summary_and_list_share_lactation_dry_heifer_calf_groups(self):
        records = self.records()
        self.assertEqual({r['tag']:r['group'] for r in records},{'TR580000000001':'lactating','TR580000000002':'dry','TR580000000003':'heifer','TR580000000004':'male','TR580000000005':'calf'})
        text = ref.home(vars(server),'admin',self.icon,mobile_ui.task_url)
        self.assertIn('<small>Genel</small><b>5</b>',text)
        self.assertIn('<small>Kuru</small><b>1</b>',text)
        self.assertEqual(text.count('class="cp-ref-stat '),6)
        text = ref.list_markup(vars(server),'/all-animals?group=dry',self.icon)
        self.assertIn('TR580000000002',text)
        self.assertNotIn('TR580000000001',text)

    def test_inactive_lost_and_promoted_records_are_excluded(self):
        with server.db() as c:
            c.execute("update animals set status='Satıldı' where id=?",(self.male,))
            c.execute("insert into animal_losses(animal_id,event_type,event_date,created_at,subject_type) values(?,?,?,?,'animal')",(self.heifer,'Kayıp',self.today.isoformat(),server.datetime.now().isoformat()))
            c.execute('update calves set promoted_animal_id=? where id=?',(self.milking,self.calf))
        self.assertEqual(len(self.records()),2)

    def test_old_milk_without_current_lactation_is_not_counted_as_milking(self):
        with server.db() as c:
            c.execute('insert into milk(animal_id,measure_date,liters) values(?,?,?)',(self.heifer,(self.today-timedelta(days=400)).isoformat(),1))
        r=next(r for r in self.records() if r['id']==self.heifer and r['source']=='animal')
        self.assertNotEqual(r['group'],'lactating')

    def test_birth_closes_positive_pregnancy_in_the_mobile_list_too(self):
        start = (self.today-timedelta(days=150)).isoformat()
        with server.db() as c:
            c.execute('insert into inseminations(animal_id,attempt,insemination_date,pregnancy_result,due_date) values(?,1,?,?,?)',(self.milking,start,'Pozitif',(self.today+timedelta(days=130)).isoformat()))
            c.execute('insert into inseminations(animal_id,attempt,insemination_date,pregnancy_result,due_date) values(?,1,?,?,?)',(self.dry,start,'Pozitif',(self.today+timedelta(days=130)).isoformat()))
        rows={r['tag']:r for r in self.records()}
        self.assertFalse(rows['TR580000000001']['pregnant'])
        self.assertTrue(rows['TR580000000002']['pregnant'])
        text=ref.list_markup(vars(server),'/all-animals?group=pregnant',self.icon)
        self.assertIn('TR580000000002',text)
        self.assertNotIn('TR580000000001',text)

    def test_turkish_search_kind_and_paddock_combine(self):
        text=ref.list_markup(vars(server),'/all-animals?q=İNCİ&kind=female&paddock=Sa%C4%9Fmal+%26+D%C3%BCve',self.icon)
        self.assertIn('TR580000000001',text)
        self.assertNotIn('TR580000000002',text)
        self.assertIn('1 hayvan',text)

    def test_age_sort_uses_age_and_puts_missing_birthdays_last(self):
        with server.db() as c:c.execute("insert into animals(tag,gender,status) values('TR580000000000','Erkek','Aktif')")
        text=ref.list_markup(vars(server),'/all-animals?sort=age&dir=desc',self.icon)
        self.assertLess(text.index('TR580000000001'),text.index('TR580000000004'))
        self.assertLess(text.index('TR580000000004'),text.index('TR580000000000'))

    def test_search_and_pagination_are_server_wide(self):
        with server.db() as c:
            for i in range(16):c.execute("insert into animals(tag,gender,status) values(?,'Erkek','Aktif')",('PAGINATION-'+str(i).zfill(2),))
        first=ref.list_markup(vars(server),'/all-animals?q=PAGINATION&per_page=10&page=1',self.icon)
        second=ref.list_markup(vars(server),'/all-animals?q=PAGINATION&per_page=10&page=2',self.icon)
        self.assertEqual(first.count('class="cp-ref-animal-row"'),10)
        self.assertEqual(second.count('class="cp-ref-animal-row"'),6)
        self.assertIn('PAGINATION-15',second)
        self.assertIn('q=PAGINATION&amp;per_page=10&amp;page=2',first)
        self.assertEqual(ref.list_markup(vars(server),'/all-animals?q=PAGINATION-15',self.icon).count('class="cp-ref-animal-row"'),1)

    def test_detail_uses_canonical_financial_values_and_real_targets(self):
        text=ref.detail_markup(vars(server),f'/animal?id={self.milking}',self.icon)
        with server.db() as c:
            animal=c.execute('select * from animals where id=?',(self.milking,)).fetchone()
            expected=server.animal_financial_summary(c,animal)
        self.assertIn(server.money(expected['net_profit']),text)
        self.assertIn('data-ref-legacy="growth"',text)
        self.assertIn('data-ref-legacy="operations"',text)
        self.assertIn('/paddocks?app_action=move&amp;subject=animal%3A'+str(self.milking),text)
        self.assertIn('data-ref-upload="animal"',text)
        self.assertNotIn('1.50 kg',text)
        self.assertNotIn('Pedometer',text)

    def test_health_plan_subject_and_calf_destinations_are_unambiguous(self):
        text=ref.detail_markup(vars(server),f'/calf?id={self.calf}',self.icon)
        self.assertIn('subject=calf%3A'+str(self.calf),text)
        self.assertIn('data-ref-upload="calf"',text)
        self.assertNotIn('data-ref-tab="reproduction"',text)
        self.assertNotIn('entry=calf&amp;mother=',text)

    def test_reference_content_escapes_names_and_photo_captions(self):
        with server.db() as c:c.execute('update animals set nickname=? where id=?',('<img src=x onerror=alert(1)>',self.milking))
        text=ref.detail_markup(vars(server),f'/animal?id={self.milking}',self.icon)
        self.assertIn('&lt;img src=x onerror=alert(1)&gt;',text)
        self.assertNotIn('<img src=x',text)

    def test_license_uses_the_real_expiry_key(self):
        with patch.object(server,'license_status',return_value=(True,{'expires_on':(self.today+timedelta(days=14)).isoformat()},'')):
            data=ref.profile(vars(server),'admin')
        self.assertIn('14 gün kaldı',data['license_note'])
        self.assertNotIn('92 gün',data['license_note'])

    def test_new_assets_and_screen_are_authenticated_without_replacing_core_forms(self):
        server.SESSIONS['reference-test']={'id':1,'username':'admin','role':'admin'}
        http=server.QuietThreadingHTTPServer(('127.0.0.1',0),server.App)
        threading.Thread(target=http.serve_forever,daemon=True).start()
        try:
            with patch.object(server,'license_status',return_value=(True,{},'')):
                base='http://127.0.0.1:'+str(http.server_port)
                for asset in ('reference.css','reference.js'):
                    with urllib.request.urlopen(base+'/app-assets/'+asset) as response:self.assertEqual(response.status,200)
                req=urllib.request.Request(base+'/animal?id='+str(self.milking),headers={'Cookie':'sid=reference-test'})
                with urllib.request.urlopen(req) as response:text=response.read().decode()
                self.assertIn('name="apple-mobile-web-app-status-bar-style" content="default"',text)
                self.assertIn('class="cp-ref cp-ref-detail"',text)
                self.assertIn('action="/animal/weight"',text)
                self.assertIn('action="/animal/sale"',text)
                self.assertIn('action="/animal/photo"',text)
                self.assertLess(text.index('class="animal-profile-head') if 'class="animal-profile-head' in text else text.index('animal-profile-head'),text.index('class="cp-ref cp-ref-detail"'))
                with urllib.request.urlopen(base+'/animal?id='+str(self.milking)) as response:self.assertIn('/login',response.url)
        finally:
            http.shutdown();http.server_close();server.SESSIONS.pop('reference-test',None)


if __name__=='__main__':unittest.main()
