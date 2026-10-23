"""Manual membership must never be guessed from milk records or sample counts."""
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlencode

from test_reports_import import server
import dairy_management as dairy
import mobile_reference as ref
import mobile_ui


class ManualLactationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.patch = patch.object(server,'DB',Path(self.temp.name)/'manual.db')
        self.patch.start()
        server.init_db()
        self.today = server.date.today().isoformat()
        self.ids = []
        with server.db() as c:
            for i in range(15):
                aid = c.execute("insert into animals(tag,gender,status,birth_date) values(?,'Dişi','Aktif','2020-01-01')",('MANUAL-'+str(i).zfill(2),)).lastrowid
                self.ids.append(aid)
                c.execute('insert into milk(animal_id,measure_date,liters) values(?,?,?)',(aid,self.today,25))
            self.male = c.execute("insert into animals(tag,gender,status) values('MALE','Erkek','Aktif')").lastrowid
            self.calf = c.execute("insert into calves(tag,gender,status,birth_date,mother_id) values('CALF','Erkek','Aktif',?,?)",(self.today,self.ids[0])).lastrowid

    def tearDown(self):
        self.patch.stop()
        self.temp.cleanup()

    def save(self, ids=None, status='lactating', **kwargs):
        with server.db() as c:
            return dairy.save_status(c,ids if ids is not None else [self.ids[0]],status,self.today,**kwargs)

    def state(self, aid=None):
        with server.db() as c:
            animal=c.execute('select * from animals where id=?',(aid or self.ids[0],)).fetchone()
            return dairy.current_status(c,animal)

    def test_existing_milk_and_birth_do_not_create_membership(self):
        with server.db() as c:
            self.assertEqual({r['group'] for r in ref.herd_records(vars(server),c) if r['source']=='animal' and r['gender']=='Dişi'},{'female'})
            self.assertEqual(c.execute('select count(*) from animal_dairy_status').fetchone()[0],0)
        self.assertEqual(self.state()['status'],'unknown')
        self.assertIsNone(self.state()['dim'])

    def test_twelve_selected_animals_agree_in_summary_list_and_detail(self):
        self.assertEqual(self.save(self.ids[:12]),12)
        with server.db() as c:
            records=ref.herd_records(vars(server),c)
        self.assertEqual(sum(r['group']=='lactating' for r in records),12)
        self.assertEqual(self.state(self.ids[12])['status'],'unknown')
        home=ref.home(vars(server),'admin',mobile_ui.icon,mobile_ui.task_url)
        self.assertIn('<small>Sağmal</small><b>12</b>',home)
        listing=ref.list_markup(vars(server),'/all-animals?group=lactating',mobile_ui.icon)
        self.assertIn('12 hayvan',listing)
        self.assertNotIn('MANUAL-12',listing)
        detail=ref.detail_markup(vars(server),'/animal?id='+str(self.ids[0]),mobile_ui.icon)
        self.assertIn('Laktasyonda (Sağmal)',detail)
        self.assertIn('/dairy-status?animal='+str(self.ids[0]),detail)

    def test_home_male_card_and_link_exclude_male_calves(self):
        home=ref.home(vars(server),'admin',mobile_ui.icon,mobile_ui.task_url)
        self.assertIn('<small>Erkek</small><b>1</b>',home)
        self.assertIn('href="/all-animals?kind=male"',home)
        self.assertNotIn('<small>Kızgın</small>',home)
        listing=ref.list_markup(vars(server),'/all-animals?kind=male',mobile_ui.icon)
        self.assertIn('>MALE<',listing)
        self.assertNotIn('>CALF<',listing)
        self.assertIn('group=heat',ref.list_markup(vars(server),'/all-animals',mobile_ui.icon))

    def test_manual_lactation_has_no_305_or_30_day_expiry(self):
        start=(server.date.today()-timedelta(days=500)).isoformat()
        self.save(lactation_start=start)
        with server.db() as c:c.execute('delete from milk')
        self.assertEqual(self.state()['status'],'lactating')
        self.assertEqual(self.state()['dim'],500)

    def test_optional_start_and_number_are_never_invented(self):
        self.save()
        state=self.state()
        self.assertIsNone(state['lactation_start'])
        self.assertIsNone(state['lactation_number'])
        self.assertIsNone(state['dim'])

    def test_invalid_dates_and_number_leave_every_record_unchanged(self):
        tomorrow=(server.date.today()+timedelta(days=1)).isoformat()
        for kwargs in ({'lactation_start':tomorrow},{'lactation_number':'1.5'},{'lactation_number':'0'},{'lactation_start':'2010-01-01'}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):self.save(self.ids[:2],**kwargs)
        with server.db() as c:
            self.assertEqual(c.execute('select count(*) from animal_dairy_status').fetchone()[0],0)
            self.assertEqual(c.execute('select count(*) from animal_dairy_status_history').fetchone()[0],0)

    def test_invalid_member_rolls_back_the_whole_selection(self):
        with server.db() as c:
            c.execute("update animals set status='Satıldı' where id=?",(self.ids[1],))
            c.execute("insert into animal_losses(animal_id,event_type,event_date,created_at,subject_type) values(?,'Kayıp',?,?,'animal')",(self.ids[2],self.today,self.today))
        for invalid in (self.male,self.ids[1],self.ids[2],999999):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):self.save([self.ids[0],invalid])
        self.assertEqual(self.state()['status'],'unknown')

    def test_late_validation_rolls_back_an_earlier_valid_write(self):
        with server.db() as c:c.execute("update animals set birth_date='2026-10-01' where id=?",(self.ids[1],))
        with self.assertRaises(ValueError):self.save(self.ids[:2],lactation_start='2025-01-01')
        self.assertEqual(self.state()['status'],'unknown')
        with server.db() as c:self.assertEqual(c.execute('select count(*) from animal_dairy_status_history').fetchone()[0],0)

    def test_history_and_manual_dry_off_share_existing_flag(self):
        self.save(lactation_start=self.today,lactation_number='2')
        self.save(status='dry')
        self.assertEqual(self.state()['status'],'dry')
        with server.db() as c:
            self.assertEqual(c.execute('select dry_since from animals where id=?',(self.ids[0],)).fetchone()[0],self.today)
            self.assertEqual(c.execute('select count(*) from animal_dairy_status_history').fetchone()[0],2)
            c.execute('update animals set dry_since=null where id=?',(self.ids[0],))
        self.assertEqual(self.state()['status'],'unknown')
        self.save()
        self.assertEqual(self.state()['status'],'lactating')

    def test_existing_reproductive_dry_off_overrides_manual_lactation(self):
        self.save()
        with server.db() as c:c.execute('update animals set dry_since=? where id=?',(self.today,self.ids[0]))
        self.assertEqual(self.state()['status'],'dry')
        self.save()
        self.assertEqual(self.state()['status'],'lactating')

    def test_bulk_blanks_preserve_current_start_single_blanks_clear_it(self):
        self.save(lactation_start=self.today,lactation_number='3')
        self.save(bulk=True)
        self.assertEqual(self.state()['lactation_start'],self.today)
        self.assertEqual(self.state()['lactation_number'],3)
        self.save()
        self.assertIsNone(self.state()['lactation_start'])
        self.assertIsNone(self.state()['lactation_number'])

    def test_reinitialization_preserves_status_and_animal_delete_cleans_up(self):
        self.save()
        server.init_db()
        self.assertEqual(self.state()['status'],'lactating')
        with server.db() as c:
            c.execute('delete from animals where id=?',(self.ids[0],))
            self.assertEqual(c.execute('select count(*) from animal_dairy_status').fetchone()[0],0)
            self.assertEqual(c.execute('select count(*) from animal_dairy_status_history').fetchone()[0],0)

    def test_status_updates_do_not_add_milk_or_finance_rows(self):
        with server.db() as c:
            milk=c.execute('select count(*),sum(liters) from milk').fetchone()
            finance=c.execute('select count(*) from finance').fetchone()[0]
        self.save(self.ids[:12])
        with server.db() as c:
            self.assertEqual(tuple(c.execute('select count(*),sum(liters) from milk').fetchone()),tuple(milk))
            self.assertEqual(c.execute('select count(*) from finance').fetchone()[0],finance)

    def test_editor_does_not_preselect_cows_or_guess_a_start(self):
        body=dairy.page_markup(vars(server),{})
        self.assertNotIn(' checked',body)
        self.assertIn('name="lactation_start" value=""',body)
        self.assertIn('0 hayvan seçili',body)
        with self.assertRaises(ValueError):dairy.page_markup(vars(server),{'animal':[str(self.male)]})

    def test_http_routes_auth_license_and_native_bulk_post(self):
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self,*args):return None
        opener=urllib.request.build_opener(NoRedirect)
        http=server.QuietThreadingHTTPServer(('127.0.0.1',0),server.App)
        threading.Thread(target=http.serve_forever,daemon=True).start()
        server.SESSIONS['manual-test']={'id':1,'username':'admin','role':'admin'}
        base='http://127.0.0.1:'+str(http.server_port)
        def request(path, data=None, login=True):
            req=urllib.request.Request(base+path,data=data,headers={'Cookie':'sid=manual-test'} if login else {})
            try:return opener.open(req)
            except urllib.error.HTTPError as response:return response
        try:
            with patch.object(server,'license_status',return_value=(True,{},'')):
                with request('/dairy-status',login=False) as response:self.assertEqual(response.headers['Location'],'/login')
                with request('/dairy-status') as response:self.assertIn('Laktasyon Durumu',response.read().decode())
                form=[('animal_id',str(aid)) for aid in self.ids[:12]]+[('status','lactating'),('effective_date',self.today),('return_to','https://example.com')]
                with request('/dairy-status/save',urlencode(form).encode()) as response:
                    self.assertEqual(response.code,303)
                    self.assertTrue(response.headers['Location'].startswith('/all-animals?group=lactating'))
                self.assertEqual(self.state()['status'],'lactating')
            with patch.object(server,'license_status',return_value=(False,{},'Etkin lisans gerekli')):
                with request('/dairy-status') as response:self.assertTrue(response.headers['Location'].startswith('/license'))
        finally:
            http.shutdown();http.server_close();server.SESSIONS.pop('manual-test',None)


if __name__=='__main__':unittest.main()
