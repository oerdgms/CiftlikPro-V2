"""Integration checks for planning, clinical records, expenses and shared tasks."""
import json
import re
import secrets
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlencode

from test_reports_import import server
import reproduction_sync as sync
import mobile_ui


class SynchronizationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.dbpatch=patch.object(server,'DB',Path(self.temp.name)/'sync.db')
        self.dbpatch.start()
        self.clock=patch.object(sync,'now',return_value=datetime(2026,10,22,10,0))
        self.clock.start()
        server.init_db()
        with server.db() as c:
            self.cow=c.execute("insert into animals(tag,gender,status,birth_date) values('COW','Dişi','Aktif','2020-01-01')").lastrowid
            self.other=c.execute("insert into animals(tag,gender,status,birth_date) values('OTHER','Dişi','Aktif','2020-01-01')").lastrowid
            self.heifer=c.execute("insert into animals(tag,gender,status,birth_date) values('HEIFER','Dişi','Aktif','2024-01-01')").lastrowid
            c.execute("insert into animal_dairy_status(animal_id,status,effective_date,updated_at,updated_by) values(?,'heifer','2026-10-01','2026-10-01','admin')",(self.heifer,))
            self.male=c.execute("insert into animals(tag,gender,status) values('MALE','Erkek','Aktif')").lastrowid
            self.pregnant=c.execute("insert into animals(tag,gender,status) values('PREGNANT','Dişi','Aktif')").lastrowid
            c.execute("insert into inseminations(animal_id,attempt,insemination_date,pregnancy_result) values(?,1,'2026-08-01','Pozitif')",(self.pregnant,))
            self.waiting=c.execute("insert into animals(tag,gender,status) values('WAITING','Dişi','Aktif')").lastrowid
            c.execute("insert into inseminations(animal_id,attempt,insemination_date,pregnancy_result) values(?,1,'2026-10-01','Bekleniyor')",(self.waiting,))
            c.execute("insert into calves(tag,mother_id,birth_date,gender) values('NEWBORN',?,'2026-10-01','Dişi')",(self.cow,))

    def tearDown(self):
        self.clock.stop();self.dbpatch.stop();self.temp.cleanup()

    def form(self,**kwargs):
        data={'protocol_key':'custom','target_group':'all','title':'Ekim grubu',
            'start_at':'2026-10-22T09:00','steps_json':json.dumps([sync.step(0,'İlk kontrol',kind='check')]),
            'vet_fee':'200','hormone_fee':'50','request_key':secrets.token_urlsafe(24),
            'veterinary_review':'yes','veterinarian':'Hekim'}
        data.update(kwargs)
        return data

    def save(self,ids=None,**kwargs):
        with server.db() as c:return sync.save_plan(vars(server),c,self.form(**kwargs),ids or [self.cow],'admin')

    def tasks(self,pid):
        with server.db() as c:return [dict(r) for r in c.execute('''select s.*,a.animal_id from repro_sync_steps s
            join repro_sync_animals a on a.id=s.enrollment_id where a.plan_id=? order by a.id,s.step_no''',(pid,))]

    def action(self,pid,action,**kwargs):
        if kwargs.get('step_id') and 'step_revision' not in kwargs:
            with server.db() as c:kwargs['step_revision']=sync.task_record(c,kwargs['step_id'])['revision']
        with server.db() as c:return sync.perform_action(vars(server),c,{'plan_id':str(pid),'action':action,**kwargs},'admin')

    def count(self,table):
        with server.db() as c:return c.execute('select count(*) from '+table).fetchone()[0]

    def test_templates_contain_timing_but_no_automatic_product_dose(self):
        for p in sync.PROTOCOLS.values():
            for row in p['steps']:
                self.assertEqual(row['dose'],'');self.assertEqual(row['product'],'')
        pid=self.save(protocol_key='ovsynch56',steps_json=json.dumps(sync.PROTOCOLS['ovsynch56']['steps']),start_at='2026-10-22T18:30')
        times=[t['planned_at'] for t in self.tasks(pid)]
        self.assertEqual(times,['2026-10-22T18:30','2026-10-29T18:30','2026-11-01T02:30','2026-11-01T18:30'])
        double=sync.PROTOCOLS['double_ovsynch']['steps']
        self.assertEqual(double[-1]['offset_minutes'],27*1440)
        self.assertEqual(sync.PROTOCOLS['cidr5_2pgf']['steps'][-1]['offset_minutes'],8*1440)

    def test_creation_is_planning_only_and_idempotent(self):
        data=self.form()
        with server.db() as c:first=sync.save_plan(vars(server),c,data,[self.cow,self.other],'admin')
        with server.db() as c:second=sync.save_plan(vars(server),c,data,[self.cow,self.other],'admin')
        self.assertEqual(first,second)
        self.assertEqual(self.count('repro_sync_plans'),1)
        self.assertEqual(self.count('repro_sync_steps'),2)
        self.assertEqual(self.count('health'),0);self.assertEqual(self.count('finance'),0)

    def test_selection_rejects_pregnant_waiting_male_and_inactive_atomically(self):
        with server.db() as c:
            sold=c.execute("insert into animals(tag,gender,status) values('SOLD','Dişi','Satıldı')").lastrowid
            lost=c.execute("insert into animals(tag,gender,status) values('LOST','Dişi','Aktif')").lastrowid
            c.execute("insert into animal_losses(subject_type,animal_id,event_date,event_type,created_at) values('animal',?,'2026-10-01','Kayıp','2026-10-01')",(lost,))
        for invalid in [self.pregnant,self.waiting,self.male,sold,lost,99999]:
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):self.save([self.cow,invalid])
        self.assertEqual(self.count('repro_sync_plans'),0)
        self.save()
        with self.assertRaises(ValueError):self.save()
        self.assertEqual(self.count('repro_sync_plans'),1)

    def test_birth_and_explicit_heifer_status_drive_filters(self):
        with server.db() as c:animals={r['id']:r for r in sync.animal_rows(vars(server),c)}
        self.assertEqual(animals[self.cow]['postpartum_days'],21)
        self.assertEqual(animals[self.heifer]['group'],'heifer')
        self.assertEqual(animals[self.other]['group'],'open')
        self.save(target_group='postpartum')
        with self.assertRaises(ValueError):self.save([self.other],target_group='heifer')
        with self.assertRaises(ValueError):self.save([self.heifer],protocol_key='ovsynch56')
        self.save([self.heifer],protocol_key='cidr5_1pgf',target_group='heifer')

    def test_every_animal_has_an_exact_time_task_and_direct_link(self):
        pid=self.save([self.cow,self.other],start_at='2026-10-22T10:30')
        with server.db() as c:rows=[r for r in server.health_plan_entries(c) if r['source']=='synchronization']
        self.assertEqual(len(rows),2)
        self.assertEqual({r['subject'] for r in rows},{'COW','OTHER'})
        self.assertTrue(all(r['state']=='today' and '10:30' in r['detail'] for r in rows))
        self.assertTrue(all(mobile_ui.task_url(r).startswith('/synchronization?plan='+str(pid)) for r in rows))
        with patch.object(sync,'now',return_value=datetime(2026,10,22,10,31)):
            with server.db() as c:rows=sync.task_entries(vars(server),c)
        self.assertTrue(all(r['state']=='overdue' for r in rows))
        with server.db() as c:self.assertEqual(sync.task_entries(vars(server),c,horizon_days=-1),[])

    def test_application_records_actual_time_once_without_shifting_future(self):
        steps=[sync.step(0,'İlaç','GnRH'),sync.step(24,'Sonraki kontrol',kind='check')]
        pid=self.save(steps_json=json.dumps(steps));tasks=self.tasks(pid)
        with self.assertRaises(ValueError):self.action(pid,'complete',step_id=tasks[0]['id'],applied_at='2026-10-22T09:45')
        self.action(pid,'complete',step_id=tasks[0]['id'],applied_at='2026-10-22T09:45',product='Hekimin ürünü',dose='2,5',unit='ml',route='IM')
        self.action(pid,'complete',step_id=tasks[0]['id'],applied_at='2026-10-22T09:45',product='Tekrar')
        self.assertEqual(self.count('health'),1)
        actual=self.tasks(pid)
        self.assertEqual(actual[0]['applied_at'],'2026-10-22T09:45')
        self.assertEqual(actual[0]['dose'],'2.5')
        self.assertEqual(actual[1]['planned_at'],'2026-10-23T09:00')
        self.assertEqual(self.count('finance'),0)

    def test_out_of_order_future_and_invalid_doses_do_not_record_applications(self):
        pid=self.save(steps_json=json.dumps([sync.step(0,'A',kind='check'),sync.step(1,'B',kind='check')]))
        with self.assertRaises(ValueError):self.action(pid,'complete',step_id=self.tasks(pid)[1]['id'],applied_at='2026-10-22T10:00')
        with self.assertRaises(ValueError):self.action(pid,'complete',step_id=self.tasks(pid)[0]['id'],applied_at='2026-10-22T10:01')
        for value in ['nan','inf','-2','0','hello']:
            with self.assertRaises(ValueError):sync.dose_value(value,True)
        self.assertEqual(self.count('health'),0)

    def test_finance_is_explicit_per_animal_and_never_duplicated(self):
        pid=self.save([self.cow,self.other],vet_fee='200,10',hormone_fee='50,25')
        self.assertEqual(self.count('finance'),0)
        for _ in range(2):self.action(pid,'finance',expense_at='2026-10-22T10:00')
        with server.db() as c:records=c.execute('select * from finance').fetchall()
        self.assertEqual(len(records),2)
        self.assertEqual({r['animal_id'] for r in records},{self.cow,self.other})
        self.assertTrue(all(r['amount']==250.35 and r['tx_type']=='Gider' for r in records))
        self.assertEqual(self.count('health'),0)
        with self.assertRaises(ValueError):self.action(pid,'delete')

    def test_one_animal_can_leave_group_and_pregnancy_suppresses_pending_medicine(self):
        pid=self.save([self.cow,self.other],steps_json=json.dumps([sync.step(0,'Hormon')]))
        with server.db() as c:eid=c.execute('select id from repro_sync_animals where animal_id=?',(self.cow,)).fetchone()[0]
        self.action(pid,'cancel_animal',enrollment_id=eid,reason='Veteriner planı değişti')
        with server.db() as c:rows=sync.task_entries(vars(server),c)
        self.assertEqual([r['subject'] for r in rows],['OTHER'])
        with server.db() as c:c.execute("insert into inseminations(animal_id,attempt,insemination_date,pregnancy_result) values(?,1,'2026-10-15','Pozitif')",(self.other,))
        with server.db() as c:self.assertEqual(sync.task_entries(vars(server),c),[])
        with self.assertRaises(ValueError):self.action(pid,'complete',step_id=self.tasks(pid)[1]['id'],applied_at='2026-10-22T10:00',product='Ürün',dose='2',unit='ml',route='IM')

    def test_edit_stale_revision_delete_and_reinitialization(self):
        pid=self.save()
        with self.assertRaises(ValueError):self.save(id=str(pid),revision='0')
        self.save(id=str(pid),revision='1',title='Yeni başlık')
        server.init_db()
        self.assertEqual(self.count('repro_sync_plans'),1)
        self.action(pid,'delete')
        self.assertEqual(self.count('repro_sync_steps'),0)
        self.assertEqual(self.count('repro_sync_animals'),0)

    def test_step_edit_is_local_and_keeps_an_audit_trail(self):
        pid=self.save([self.cow,self.other]);tasks=self.tasks(pid)
        with self.assertRaises(ValueError):self.action(pid,'update_step',step_id=tasks[0]['id'],planned_at='2026-10-23T11:30')
        self.action(pid,'update_step',step_id=tasks[0]['id'],planned_at='2026-10-23T11:30',note='Veteriner takvimi değiştirdi')
        self.assertEqual(self.tasks(pid)[0]['planned_at'],'2026-10-23T11:30')
        self.assertEqual(self.tasks(pid)[1]['planned_at'],'2026-10-22T09:00')
        self.assertEqual(self.count('repro_sync_events'),2)
        with self.assertRaisesRegex(ValueError,'başka bir ekranda'):
            self.action(pid,'update_step',step_id=tasks[0]['id'],step_revision='1',planned_at='2026-10-24T11:30',note='Eski ekran')

    def test_insemination_requires_explicit_action_and_reuses_same_day_record(self):
        pid=self.save(steps_json=json.dumps([sync.step(0,'Tohumlama',kind='insemination')]))
        tid=self.tasks(pid)[0]['id']
        with self.assertRaises(ValueError):self.action(pid,'complete',step_id=tid,applied_at='2026-10-22T09:30')
        with server.db() as c:existing=c.execute("insert into inseminations(animal_id,attempt,insemination_date,pregnancy_result) values(?,1,'2026-10-22','Bekleniyor')",(self.cow,)).lastrowid
        self.action(pid,'complete',step_id=tid,applied_at='2026-10-22T09:30',confirm_insemination='yes')
        self.assertEqual(self.tasks(pid)[0]['insemination_id'],existing)
        self.assertEqual(self.count('inseminations'),3)  # initial pregnant + initial waiting + actual cow
        self.assertEqual(self.count('health'),1)

    def test_html_escapes_user_text_and_native_routes_authorize_and_dedupe(self):
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self,*args):return None
        opener=urllib.request.build_opener(NoRedirect)
        http=server.QuietThreadingHTTPServer(('127.0.0.1',0),server.App)
        threading.Thread(target=http.serve_forever,daemon=True).start()
        server.SESSIONS['sync-test']={'id':1,'username':'admin','role':'admin'}
        base='http://127.0.0.1:'+str(http.server_port)
        def request(path,data=None,login=True):
            req=urllib.request.Request(base+path,data=urlencode(data,doseq=True).encode() if data is not None else None,headers={'Cookie':'sid=sync-test'} if login else {})
            try:return opener.open(req)
            except urllib.error.HTTPError as response:return response
        try:
            with patch.object(server,'license_status',return_value=(True,{},'')):
                with request('/synchronization',login=False) as response:self.assertEqual(response.headers['Location'],'/login')
                with request('/synchronization') as response:
                    document=response.read().decode()
                    self.assertIn('Senkronizasyon Tanımla',document)
                    csrf=re.search(r'name="csrf" value="([^"]+)"',document).group(1)
                form=self.form(title='<script>alert(1)</script>');form['animal_id']=[str(self.cow)]
                with request('/synchronization/save',form) as response:self.assertIn('Oturum',response.headers['Location'])
                self.assertEqual(self.count('repro_sync_plans'),0)
                form['csrf']=csrf
                for _ in range(2):
                    with request('/synchronization/save',form) as response:self.assertEqual(response.code,303)
                self.assertEqual(self.count('repro_sync_plans'),1)
                for asset in ['synchronization.js','synchronization.css']:
                    with request('/app-assets/'+asset) as response:self.assertEqual(response.code,200)
                with request('/synchronization?plan=1') as response:
                    document=response.read().decode();self.assertNotIn('<script>alert(1)</script>',document);self.assertIn('&lt;script&gt;',document)
                with request('/synchronization?plan=nan') as response:self.assertEqual(response.code,303)
            with patch.object(server,'license_status',return_value=(False,{},'Lisans gerekli')):
                with request('/synchronization') as response:self.assertTrue(response.headers['Location'].startswith('/license'))
        finally:
            http.shutdown();http.server_close();server.SESSIONS.pop('sync-test',None)


if __name__=='__main__':unittest.main()
