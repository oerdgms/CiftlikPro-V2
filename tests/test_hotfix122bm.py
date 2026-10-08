import json, tempfile, threading, unittest, urllib.parse, urllib.request
from datetime import date
from pathlib import Path
from unittest.mock import patch
from test_reports_import import server

class Hotfix122BMTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.db_patch=patch.object(server,'DB',Path(self.temp.name)/'test.db'); self.db_patch.start()
        server.init_db()
        with server.db() as c:
            self.ids=[]
            for i in range(1,4):
                cur=c.execute("insert into animals(tag,gender,status,paddock) values(?,'Dişi','Aktif','SA1')",(f'TRBM{i:03d}',))
                self.ids.append(cur.lastrowid)
        server.SESSIONS['bm-test']={'username':'admin','role':'admin'}
        self.http=server.QuietThreadingHTTPServer(('127.0.0.1',0),server.App)
        threading.Thread(target=self.http.serve_forever,daemon=True).start()
    def tearDown(self):
        self.http.shutdown(); self.http.server_close(); server.SESSIONS.pop('bm-test',None)
        self.db_patch.stop(); self.temp.cleanup()
    def _get(self,path):
        req=urllib.request.Request(f'http://127.0.0.1:{self.http.server_port}{path}',headers={'Cookie':'sid=bm-test'})
        with patch.object(server,'license_status',return_value=(True,{},'')):
            with urllib.request.urlopen(req,timeout=20) as r:return r.read().decode(),r.geturl()
    def _post(self,path,data):
        req=urllib.request.Request(f'http://127.0.0.1:{self.http.server_port}{path}',data=urllib.parse.urlencode(data).encode(),method='POST',headers={'Cookie':'sid=bm-test','Content-Type':'application/x-www-form-urlencoded'})
        with patch.object(server,'license_status',return_value=(True,{},'')):
            with urllib.request.urlopen(req,timeout=20) as r:return r.read().decode(),r.geturl()
    def test_multi_selector_is_present_and_compact(self):
        html,_=self._get('/health')
        self.assertIn('<option value="multi">Birden Fazla Hayvan</option>',html)
        self.assertIn('id="healthMultiSearch"',html)
        self.assertIn('id="healthMultiAdd"',html)
        self.assertIn('id="healthMultiSelected"',html)
        self.assertIn('Seçilen: 0 hayvan',html)
    def test_multi_vaccine_plan_creates_one_course_and_tasks_for_each_selected_animal(self):
        keys=[f'A:{x}' for x in self.ids]
        self._post('/health',{
            'scope_type':'multi','subject_keys_json':json.dumps(keys),'kind':'Aşı','product':'BM Çoklu Aşı',
            'applied_date':date.today().isoformat(),'dose_count':'2','dose_interval_days':'15','cost':'10','notes':'çoklu test'
        })
        with server.db() as c:
            course=c.execute("select * from health_courses where product='BM Çoklu Aşı'").fetchone()
            self.assertIsNotNone(course); self.assertEqual(course['scope_type'],'multi')
            tasks=c.execute('select * from health_tasks where course_id=? order by id',(course['id'],)).fetchall()
        self.assertEqual(len(tasks),6)
        self.assertEqual({t['animal_id'] for t in tasks},set(self.ids))
        self.assertEqual({t['dose_no'] for t in tasks},{1,2})
        html,_=self._get('/health')
        self.assertIn('👥 Çoklu Hayvan Planı',html)
        self.assertIn('3 hayvan · 1 / 2. doz',html)
        self.assertIn('✅ 3 Hayvan Yapıldı',html)
    def test_batch_done_writes_health_history_for_all_selected_animals(self):
        keys=[f'A:{x}' for x in self.ids[:2]]
        self._post('/health',{
            'scope_type':'multi','subject_keys_json':json.dumps(keys),'kind':'Aşı','product':'BM Tamamla',
            'applied_date':date.today().isoformat(),'dose_count':'1','dose_interval_days':'15','cost':'0','notes':''
        })
        with server.db() as c:
            course=c.execute("select * from health_courses where product='BM Tamamla'").fetchone()
        self._post('/health/task-batch-done',{
            'course_id':course['id'],'planned_date':date.today().isoformat(),'dose_no':'1','day_no':'1','application_no':'1'
        })
        with server.db() as c:
            rows=c.execute("select animal_id from health where course_id=? order by animal_id",(course['id'],)).fetchall()
            pending=c.execute("select count(*) from health_tasks where course_id=? and status='Bekliyor'",(course['id'],)).fetchone()[0]
        self.assertEqual([r['animal_id'] for r in rows],sorted(self.ids[:2]))
        self.assertEqual(pending,0)
    def test_multi_requires_at_least_two_active_targets(self):
        _,url=self._post('/health',{
            'scope_type':'multi','subject_keys_json':json.dumps([f'A:{self.ids[0]}']),'kind':'Aşı','product':'BM Tek',
            'applied_date':date.today().isoformat(),'dose_count':'1','dose_interval_days':'15','cost':'0','notes':''
        })
        self.assertIn('msg=',url)
        with server.db() as c:self.assertEqual(c.execute("select count(*) from health_courses where product='BM Tek'").fetchone()[0],0)
    def test_version(self):
        self.assertEqual(server.APP_VERSION,'3.9.23 DEV4 Hotfix1.22bs')
        self.assertEqual(server.APP_LABEL,'v3.9.23 DEV4 Hotfix1.22bs')

if __name__=='__main__': unittest.main()
