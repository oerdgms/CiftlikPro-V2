"""Health ledger, recurring plans and responsive route integration checks."""
import json
import re
import secrets
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlencode

from test_reports_import import server
import health_center as hc
import health_views as views
import reproduction_sync as sync


class UnifiedHealthTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.dbpatch=patch.object(server,'DB',Path(self.temp.name)/'health.db');self.dbpatch.start()
        self.clock=patch.object(sync,'now',return_value=datetime(2026,10,22,15,0));self.clock.start()
        server.init_db()
        with server.db() as c:
            self.pad=c.execute("insert into paddocks(name,capacity,created_at) values('Sağmal 1',50,'2026-10-22')").lastrowid
            self.a=c.execute("insert into animals(tag,nickname,gender,status,paddock_id) values('TR001','Boncuk','Dişi','Aktif',?)",(self.pad,)).lastrowid
            self.b=c.execute("insert into animals(tag,gender,status) values('TR002','Erkek','Aktif')").lastrowid
            self.calf=c.execute("insert into calves(tag,mother_id,birth_date,gender,status) values('CALF',?,'2026-10-01','Dişi','Aktif')",(self.a,)).lastrowid
        self.refs=['animal:'+str(self.a),'calf:'+str(self.calf)]

    def tearDown(self):
        self.clock.stop();self.dbpatch.stop();self.temp.cleanup()

    def form(self,**changes):
        result={'category':'vaccine','product':'Şap <Deneme>','start_date':'2026-10-22',
            'subjects_json':json.dumps(self.refs),'request_key':secrets.token_urlsafe(24),
            'repeat_value':'6','repeat_unit':'months','rapel':'yes','rapel_days':'21','cost':'12.35'}
        result.update(changes);return result

    def save(self,**changes):
        with server.db() as c:return hc.save_program(vars(server),c,self.form(**changes),'admin')

    def tasks(self,pid):
        with server.db() as c:return [dict(r) for r in c.execute('select * from health_tasks where course_id=? order by cycle_no,dose_no,id',(pid,))]

    def count(self,table):
        with server.db() as c:return c.execute('select count(*) from '+table).fetchone()[0]

    def batch(self,tasks,actual='2026-10-22',**changes):
        data={'action':'complete_batch','batch_ref':hc.batch_ref(tasks[0]),
            'task_ids':json.dumps([t['id'] for t in tasks]),'actual_date':actual}
        data.update(changes)
        with server.db() as c:return hc.action(vars(server),c,data,'admin')

    def complete(self,tid,actual='2026-10-22'):
        with server.db() as c:return hc.action(vars(server),c,{'action':'complete','task_id':str(tid),'actual_date':actual},'admin')

    def case(self,**changes):
        data={'diagnosis':'Takip edilecek belirti','illness_date':'2026-10-22','subjects_json':json.dumps(self.refs),
            'request_key':secrets.token_urlsafe(24),'veterinarian':'','vet_cost':'','medicine_cost':''}
        data.update(changes)
        with server.db() as c:return hc.save_case(vars(server),c,data,'admin')

    def test_migration_is_repeatable_and_keeps_existing_records(self):
        with server.db() as c:c.execute("insert into health(animal_id,kind,product,applied_date) values(?,'Muayene','Eski kayıt','2026-01-01')",(self.a,))
        server.init_db();server.init_db()
        self.assertEqual(self.count('health'),1)
        with server.db() as c:self.assertEqual(c.execute("select count(*) from health_definitions where category='vaccine' and name='Şap'").fetchone()[0],1)

    def test_plan_only_and_duplicate_submit_do_not_post_health_or_finance(self):
        data=self.form()
        with server.db() as c:pid=hc.save_program(vars(server),c,data,'admin')
        with server.db() as c:again=hc.save_program(vars(server),c,data,'admin')
        self.assertEqual(pid,again);self.assertEqual(len(self.tasks(pid)),4)
        self.assertEqual(self.count('health'),0);self.assertEqual(self.count('finance'),0)

    def test_bulk_67_subjects_record_once_with_individual_cost_and_actual_date_rapel(self):
        refs=list(self.refs)
        with server.db() as c:
            for n in range(65):
                aid=c.execute("insert into animals(tag,gender,status) values(?,'Dişi','Aktif')",('BULK-'+str(n),)).lastrowid
                refs.append('animal:'+str(aid))
        pid=self.save(subjects_json=json.dumps(refs),start_date='2026-10-20')
        first=[t for t in self.tasks(pid) if t['dose_no']==1]
        self.assertEqual(len(first),67)
        self.assertIn('67 hayvan',self.batch(first))
        self.assertIn('zaten yapılmış',self.batch(first))
        self.assertEqual(self.count('health'),67);self.assertEqual(self.count('finance'),67)
        with server.db() as c:
            self.assertAlmostEqual(c.execute('select sum(amount) from finance').fetchone()[0],827.45)
            self.assertEqual({r[0] for r in c.execute('select applied_date from health')},{'2026-10-22'})
        tasks=self.tasks(pid)
        self.assertEqual({t['planned_date'] for t in tasks if t['cycle_no']==1 and t['dose_no']==2},{'2026-11-12'})
        self.assertEqual({t['planned_date'] for t in tasks if t['cycle_no']==2 and t['dose_no']==1},{'2027-04-22'})

    def test_bulk_partial_selection_and_moved_paddock_keep_unselected_animals_pending(self):
        pid=self.save(start_date='2026-10-20')
        first=[t for t in self.tasks(pid) if t['dose_no']==1]
        with server.db() as c:
            c.execute('update animals set paddock_id=null where id=?',(self.a,))
            c.execute("insert into animals(tag,gender,status,paddock_id) values('NEW','Dişi','Aktif',?)",(self.pad,))
        self.batch([first[0]],task_ids=json.dumps([first[0]['id'],first[0]['id']]))
        tasks=self.tasks(pid)
        self.assertEqual(self.count('health'),1);self.assertEqual(self.count('finance'),1)
        self.assertEqual(next(t for t in tasks if t['id']==first[1]['id'])['status'],'Bekliyor')
        self.assertEqual({(t['animal_id'],t['calf_id']) for t in tasks},{(self.a,None),(None,self.calf)})

    def test_bulk_invalid_stale_or_mixed_stage_selection_is_atomic(self):
        pid=self.save();tasks=self.tasks(pid);first=[t for t in tasks if t['dose_no']==1]
        second=next(t for t in tasks if t['dose_no']==2)
        other=self.save(product='Başka plan');foreign=self.tasks(other)[0]
        for changes in [
            {'task_ids':'[]'},{'task_ids':'broken'},{'task_ids':'[true]'},
            {'task_ids':json.dumps([first[0]['id'],999999])},
            {'task_ids':json.dumps([first[0]['id'],foreign['id']])},
            {'task_ids':json.dumps([first[0]['id'],second['id']])},
            {'actual_date':'2026-10-23'},{'batch_ref':hc.batch_ref(first[0]).replace('2026-10-22','2026-10-21')},
        ]:
            with self.subTest(changes=changes),self.assertRaises(ValueError):self.batch(first,**changes)
        with self.assertRaises(ValueError):self.batch([second])
        with server.db() as c:c.execute("update calves set status='Satıldı' where id=?",(self.calf,))
        with self.assertRaises(ValueError):self.batch(first)
        self.assertEqual(self.count('health'),0);self.assertEqual(self.count('finance'),0)
        self.assertTrue(all(t['status']=='Bekliyor' for t in self.tasks(pid)))

    def test_bulk_old_multi_animal_course_also_reanchors_next_dose(self):
        with server.db() as c:
            pid=c.execute("insert into health_courses(kind,product,scope_type,start_date,dose_count,interval_days,cost_per_application,created_at) values('Aşı','Eski şap','multi','2026-10-20',2,21,12.35,'2026-10-20')").lastrowid
            server.create_health_course_tasks(c,pid,[(self.a,None,'TR001'),(None,self.calf,'CALF')],'Aşı','2026-10-20',12.35,'',dose_count=2,interval_days=21)
        first=[t for t in self.tasks(pid) if t['dose_no']==1]
        self.batch(first);self.batch(first)
        self.assertEqual(self.count('health'),2);self.assertEqual(self.count('finance'),2)
        self.assertEqual({t['planned_date'] for t in self.tasks(pid) if t['dose_no']==2},{'2026-11-12'})
        with server.db() as c:self.assertIsNone(c.execute('select 1 from health_program_meta where course_id=?',(pid,)).fetchone())

    def test_bulk_treatment_keeps_days_and_daily_applications_separate(self):
        pid=self.save(category='treatment',schedule_mode='course',treatment_days='2',times_per_day='2')
        tasks=self.tasks(pid)
        slot=lambda day,app:[t for t in tasks if t['day_no']==day and t['application_no']==app]
        with self.assertRaises(ValueError):self.batch(slot(1,2))
        self.batch(slot(1,1))
        with self.assertRaises(ValueError):self.batch(slot(1,2),actual='2026-10-21')
        with self.assertRaises(ValueError):self.batch(slot(2,1))
        self.batch(slot(1,2))
        self.assertEqual(self.count('health'),4)
        self.assertTrue(all(t['status']=='Bekliyor' for t in self.tasks(pid) if t['day_no']==2))

    def test_bulk_parasite_and_vitamin_and_paused_program(self):
        for category in ['parasite','vitamin']:
            pid=self.save(category=category,rapel='no',repeat_value='0')
            self.batch(self.tasks(pid))
        self.assertEqual(self.count('health'),4)
        pid=self.save();first=[t for t in self.tasks(pid) if t['dose_no']==1]
        with server.db() as c:hc.action(vars(server),c,{'action':'pause','course_id':str(pid)},'admin')
        with self.assertRaises(ValueError):self.batch(first)
        self.assertEqual(self.count('health'),4)

    def test_bulk_preview_contains_all_67_animals_beyond_paginated_rows(self):
        refs=list(self.refs)
        with server.db() as c:
            for n in range(65):
                aid=c.execute("insert into animals(tag,gender,status) values(?,'Dişi','Aktif')",('PREVIEW-'+str(n),)).lastrowid
                refs.append('animal:'+str(aid))
        pid=self.save(subjects_json=json.dumps(refs))
        with server.db() as c:page=views.markup(vars(server),c,{'category':['vaccine'],'plan':[str(pid)]},'token')
        payload=json.loads(re.search(r'<script type="application/json" id="hcBatchData">(.*?)</script>',page,re.S)[1])
        self.assertEqual(len(payload),1)
        self.assertEqual(len(next(iter(payload.values()))['members']),67)
        self.assertEqual(page.count('<article class="hc-task"'),25)
        self.assertIn('Toplu Yapıldı',page)
        self.assertNotIn('<Deneme>',page)

    def test_all_categories_and_mixed_subject_types(self):
        for category,kind in hc.KINDS.items():
            pid=self.save(category=category,rapel='no',repeat_value='0')
            with server.db() as c:
                self.assertEqual(c.execute('select kind from health_courses where id=?',(pid,)).fetchone()[0],kind)
                rows=[r for r in hc.workspace_data(vars(server),c)['pending'] if r.get('course_id')==pid]
            self.assertEqual(len(rows),2);self.assertTrue(all(r['category']==category for r in rows))

    def test_recurrence_and_rapel_follow_actual_date_and_snapshot_animal_ids(self):
        pid=self.save(start_date='2026-10-20')
        first=next(t for t in self.tasks(pid) if t['animal_id']==self.a and t['dose_no']==1)
        with server.db() as c:
            c.execute('update animals set paddock_id=null where id=?',(self.a,))
            c.execute("insert into animals(tag,gender,status,paddock_id) values('NEW','Dişi','Aktif',?)",(self.pad,))
        self.complete(first['id'])
        self.complete(first['id'])
        tasks=self.tasks(pid)
        self.assertEqual(len(tasks),6)
        self.assertEqual({(t['animal_id'],t['calf_id']) for t in tasks},{(self.a,None),(None,self.calf)})
        rapel=next(t for t in tasks if t['animal_id']==self.a and t['cycle_no']==1 and t['dose_no']==2)
        self.assertEqual(rapel['planned_date'],'2026-11-12')
        repeat=next(t for t in tasks if t['animal_id']==self.a and t['cycle_no']==2 and t['dose_no']==1)
        self.assertEqual(repeat['planned_date'],'2027-04-22')
        self.assertEqual(self.count('health'),1);self.assertEqual(self.count('finance'),1)
        with server.db() as c:self.assertEqual(c.execute('select amount from finance').fetchone()[0],12.35)

    def test_repeat_months_respect_month_end_and_days_are_distinct(self):
        self.assertEqual(hc.add_interval(date(2026,1,31),1,'months'),date(2026,2,28))
        self.assertEqual(hc.add_interval(date(2028,1,31),1,'months'),date(2028,2,29))
        self.assertEqual(hc.add_interval(date(2026,1,31),30,'days'),date(2026,3,2))

    def test_invalid_and_future_record_roll_back_all_changes(self):
        for changes in [{'mode':'record','start_date':'2026-10-23'},{'cost':'NaN'},
                        {'repeat_value':'1','repeat_unit':'days','rapel_days':'21'},
                        {'subjects_json':'["animal:999999"]'}]:
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):self.save(**changes)
        self.assertEqual(self.count('health_courses'),0);self.assertEqual(self.count('health_tasks'),0)
        self.assertEqual(self.count('finance'),0)

    def test_rapel_cannot_complete_before_first_application(self):
        pid=self.save();rapel=next(t for t in self.tasks(pid) if t['dose_no']==2)
        with self.assertRaises(ValueError):self.complete(rapel['id'])
        self.assertEqual(self.count('health'),0)

    def test_stale_edits_and_completed_schedule_are_protected(self):
        pid=self.save()
        data=self.form(id=str(pid),revision='1',product='Güncel ad')
        with server.db() as c:hc.save_program(vars(server),c,data,'admin')
        with self.assertRaises(ValueError):
            with server.db() as c:hc.save_program(vars(server),c,data,'admin')
        self.complete(self.tasks(pid)[0]['id'])
        with self.assertRaises(ValueError):
            with server.db() as c:hc.save_program(vars(server),c,self.form(id=str(pid),revision='2',start_date='2026-10-21'),'admin')

    def test_pause_delete_and_undo_keep_ledger_and_money_consistent(self):
        pid=self.save();first=self.tasks(pid)[0];self.complete(first['id'])
        with server.db() as c:hc.action(vars(server),c,{'action':'delete_record','health_id':1},'admin')
        self.assertEqual(self.count('health'),0);self.assertEqual(self.count('finance'),0)
        self.assertEqual(len(self.tasks(pid)),4)
        self.complete(first['id'])
        with server.db() as c:
            hc.action(vars(server),c,{'action':'pause','course_id':pid},'admin')
        with server.db() as c:self.assertFalse(hc.workspace_data(vars(server),c)['pending'])
        with server.db() as c:hc.action(vars(server),c,{'action':'delete_program','course_id':pid},'admin')
        self.assertEqual(self.count('health'),1);self.assertEqual(self.count('finance'),1)
        self.assertTrue(all(t['status']!='Bekliyor' for t in self.tasks(pid)))

    def test_applied_record_edit_updates_single_finance_entry(self):
        pid=self.save();self.complete(self.tasks(pid)[0]['id'])
        with server.db() as c:hc.edit_record(vars(server),c,{'id':1,'applied_date':'2026-10-22','product':'Düzeltilmiş ad','cost':'10','notes':'Düzeltme'},'admin')
        self.assertEqual(self.count('finance'),1)
        with server.db() as c:self.assertEqual(c.execute('select amount from finance').fetchone()[0],10)
        with self.assertRaises(ValueError):
            with server.db() as c:hc.edit_record(vars(server),c,{'id':1,'applied_date':'2026-10-21'},'admin')

    def test_disease_optional_costs_and_exact_total_distribution(self):
        cid=self.case(vet_cost='100.01')
        self.assertEqual(self.count('health_cases'),1);self.assertEqual(self.count('health'),2)
        with server.db() as c:
            amounts=[r[0] for r in c.execute('select amount from finance')]
            data=hc.workspace_data(vars(server),c)
        self.assertAlmostEqual(sum(amounts),100.01);self.assertEqual(data['patient_count'],2)
        other=self.case(subjects_json=json.dumps(['animal:'+str(self.a)]))
        with server.db() as c:self.assertEqual(hc.workspace_data(vars(server),c)['patient_count'],2)
        with server.db() as c:hc.action(vars(server),c,{'action':'close_case','case_id':cid},'admin')
        with server.db() as c:self.assertEqual(hc.workspace_data(vars(server),c)['patient_count'],1)
        with server.db() as c:hc.action(vars(server),c,{'action':'delete_case','case_id':cid},'admin')
        self.assertEqual(self.count('finance'),0);self.assertEqual(self.count('health'),1)

    def test_views_include_real_month_calendar_and_escape_user_text(self):
        self.save(product='<script>alert(1)</script>')
        self.case(diagnosis='<img src=x onerror=alert(1)>')
        with server.db() as c:
            for category in ['general',*hc.CATEGORIES]:
                page=views.markup(vars(server),c,{'category':[category]},'token')
                self.assertIn('id="healthCenter"',page);self.assertNotIn('<script>alert(1)</script>',page)
                self.assertNotIn('<img src=x onerror',page)
            page=views.markup(vars(server),c,{'view':['calendar'],'month':['2026-10'],'date':['2026-10-22']},'token')
        self.assertIn('Ekim 2026',page);self.assertIn('hc-calendar-day selected today',page)
        self.assertIn('TR001',page);self.assertIn('CALF',page)
        self.assertIn('&lt;script&gt;',page)

    def test_legacy_sources_and_history_survive_the_new_workspace(self):
        with server.db() as c:
            c.execute("insert into health(animal_id,kind,product,applied_date,next_date) values(?,'Aşı','Önceki aşı','2026-10-01','2026-10-22')",(self.a,))
            for i in range(6):c.execute("insert into health(animal_id,kind,product,next_date) values(?,'Muayene',?,'2026-10-22')",(self.a,'Eski plan '+str(i)))
        with server.db() as c:
            data=hc.workspace_data(vars(server),c)
            self.assertEqual(len(data['pending']),7)
            self.assertEqual(len(data['history']),1)
            self.assertIn('Eski plan 5',views.markup(vars(server),c,{},'token'))

    def test_finite_treatment_days_and_daily_applications_are_retained(self):
        pid=self.save(category='treatment',schedule_mode='course',treatment_days='2',treatment_interval_days='9',times_per_day='2',rapel='no',repeat_value='0')
        tasks=self.tasks(pid)
        self.assertEqual(len(tasks),8)
        self.assertEqual({t['planned_date'] for t in tasks},{'2026-10-22','2026-10-31'})
        self.assertEqual({t['application_no'] for t in tasks},{1,2})
        self.complete(tasks[0]['id'])
        self.assertEqual(len(self.tasks(pid)),8)
        self.assertEqual(self.count('health'),1)

    def test_promotion_keeps_future_tasks_and_active_disease_on_the_same_animal(self):
        pid=self.save(subjects_json=json.dumps(['calf:'+str(self.calf)]))
        cid=self.case(subjects_json=json.dumps(['calf:'+str(self.calf)]))
        with server.db() as c:c.execute('update calves set birth_date=? where id=?',((date.today()-timedelta(days=400)).isoformat(),self.calf))
        server.promote_mature_calves()
        with server.db() as c:
            promoted=c.execute('select promoted_animal_id from calves where id=?',(self.calf,)).fetchone()[0]
            self.assertIsNotNone(promoted)
            self.assertEqual(c.execute('select animal_id from health_case_targets where case_id=?',(cid,)).fetchone()[0],promoted)
        self.assertTrue(all(t['animal_id']==promoted and t['calf_id'] is None for t in self.tasks(pid)))

    def test_history_view_shows_each_record_once(self):
        self.save(mode='record',subjects_json=json.dumps(['animal:'+str(self.a)]),rapel='no',repeat_value='0')
        with server.db() as c:page=views.markup(vars(server),c,{'tab':['done']},'token')
        self.assertEqual(page.count('class="hc-history"'),1)

    def test_http_auth_csrf_and_assets(self):
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self,*args):return None
        opener=urllib.request.build_opener(NoRedirect)
        http=server.QuietThreadingHTTPServer(('127.0.0.1',0),server.App)
        threading.Thread(target=http.serve_forever,daemon=True).start()
        server.SESSIONS['health-center-test']={'id':1,'username':'admin','role':'admin'}
        base='http://127.0.0.1:'+str(http.server_port)
        def request(path,data=None,login=True):
            req=urllib.request.Request(base+path,data=urlencode(data).encode() if data is not None else None,headers={'Cookie':'sid=health-center-test'} if login else {})
            try:return opener.open(req)
            except urllib.error.HTTPError as response:return response
        try:
            with patch.object(server,'license_status',return_value=(True,{},'')):
                with request('/health',login=False) as r:self.assertEqual(r.headers['Location'],'/login')
                with request('/health') as r:
                    page=r.read().decode();token=re.search(r'name="csrf" value="([^"]+)"',page)[1]
                    self.assertIn('Sağlık Yönetimi',page);self.assertNotIn('class="sync-entry-nav"',page)
                form=self.form()
                with request('/health-center/program',form) as r:self.assertIn('Oturum',r.headers['Location'])
                self.assertEqual(self.count('health_courses'),0)
                form['csrf']=token
                for _ in range(2):
                    with request('/health-center/program',form) as r:self.assertEqual(r.code,303)
                self.assertEqual(self.count('health_courses'),1)
                first=[t for t in self.tasks(1) if t['dose_no']==1]
                bulk={'action':'complete_batch','batch_ref':hc.batch_ref(first[0]),
                    'task_ids':json.dumps([t['id'] for t in first]),'actual_date':'2026-10-22'}
                with request('/health-center/action',bulk,login=False) as r:self.assertEqual(r.headers['Location'],'/login')
                with request('/health-center/action',bulk) as r:self.assertIn('Oturum',r.headers['Location'])
                self.assertEqual(self.count('health'),0)
                bulk['csrf']=token
                for _ in range(2):
                    with request('/health-center/action',bulk) as r:self.assertEqual(r.code,303)
                self.assertEqual(self.count('health'),2);self.assertEqual(self.count('finance'),2)
                for path in ['/health?category=sync','/health?view=calendar','/health?category=parasite&tab=done','/app-assets/health-center.css','/app-assets/health-center.js','/health-center/print?category=vaccine','/health-center/report.pdf?category=vaccine']:
                    with request(path) as r:self.assertEqual(r.code,200)
            with patch.object(server,'license_status',return_value=(False,{},'Lisans gerekli')):
                with request('/health') as r:self.assertTrue(r.headers['Location'].startswith('/license'))
        finally:
            http.shutdown();http.server_close();server.SESSIONS.pop('health-center-test',None)


if __name__=='__main__':unittest.main()
