from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
import io,json,sqlite3,tempfile,threading,unittest,urllib.error,urllib.parse,urllib.request,zipfile
from pathlib import Path
from unittest.mock import patch
from PIL import Image
import test_app_edition as app_tests
import multi_farm as farms
import release_info
server=app_tests.server
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args):return None
class MultiFarmTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.root=Path(self.temp.name);self.stack=ExitStack();self.addCleanup(self.stack.close)
  for key,filename in [('DB','ciftlik.db'),('DATA_ROOT',''),('BACKUPS','backups'),('UPLOADS','uploads')]:self.stack.enter_context(patch.object(server,key,farms.ScopedPath(self.root/filename,filename)))
  self.stack.enter_context(patch.object(server,'license_status',return_value=(True,{},'')))
  server.init_db()
  with server.db() as c:
   c.execute("update users set password=? where username='admin'",(server.password_hash('test-admin-123'),))
   c.execute("insert into users(username,password,role,active,full_name) values(?,?,?,1,?)",('staff',server.password_hash('test-staff-123'),'personel','Çalışan'))
   c.execute("insert into animals(tag,gender,status) values('FIRST-ANIMAL','Erkek','Aktif')")
  for name,role in [('admin','admin'),('staff','personel')]:
   server.SESSIONS['farm-'+name]={'id':1 if name=='admin' else 2,'username':name,'role':role}
   self.addCleanup(lambda name=name:server.SESSIONS.pop('farm-'+name,None))
  self.registry=farms.Registry(vars(server));self.http=server.QuietThreadingHTTPServer(('127.0.0.1',0),server.App)
  threading.Thread(target=self.http.serve_forever,daemon=True).start();self.base='http://127.0.0.1:'+str(self.http.server_port)
  self.addCleanup(self.http.server_close);self.addCleanup(self.http.shutdown)
 def request(self,path,fields=None,sid='farm-admin',headers=None):
  hd={'Cookie':'sid='+sid} if sid else {};hd.update(headers or {})
  req=urllib.request.Request(self.base+path,data=None if fields is None else urllib.parse.urlencode(fields).encode(),headers=hd)
  try:
   with urllib.request.build_opener(NoRedirect).open(req,timeout=30) as r:return r.status,r.headers,r.read()
  except urllib.error.HTTPError as r:return r.code,r.headers,r.read()
 def create(self,name='İkinci İşletme'):return self.registry.create(name)
 def csrf(self,sid='farm-admin'):
  self.request('/farms?farm=primary',sid=sid);return server.SESSIONS[sid]['farm_csrf']
 def seed(self,farm,tag):
  with farms.scope(farm):
   with server.db() as c:c.execute("insert into animals(tag,gender,status) values(?,'Erkek','Aktif')",(tag,))
 def test_first_database_preserved_new_is_empty_and_paths_restore(self):
  farm=self.create()
  with server.db() as c:self.assertEqual(c.execute('select tag from animals').fetchone()[0],'FIRST-ANIMAL')
  with farms.scope(farm):
   self.assertEqual(Path(server.DB),Path(farm['directory'])/'ciftlik.db')
   self.assertEqual(Path(server.UPLOADS),Path(farm['directory'])/'uploads')
   with server.db() as c:self.assertEqual(c.execute('select count(*) from animals').fetchone()[0],0)
  self.assertEqual(Path(server.DB),self.root/'ciftlik.db')
  self.assertTrue((self.root/'enterprise-index-backups/enterprises-last.sqlite3').exists())
 def test_http_create_switch_csrf_and_staff_cannot_create(self):
  token=self.csrf()
  self.assertEqual(self.request('/farms/create?farm=primary',{'name':'Denied','csrf':'bad'})[0],403)
  status,headers,_=self.request('/farms/create?farm=primary',{'name':'Yeni Çiftlik','csrf':token});self.assertEqual(status,303)
  target=urllib.parse.parse_qs(urllib.parse.urlsplit(headers['Location']).query)['farm'][0]
  self.assertEqual(server.SESSIONS['farm-admin']['active_farm'],target)
  status,_,body=self.request('/all-animals?farm='+target);self.assertEqual(status,200);self.assertNotIn('FIRST-ANIMAL',body.decode());self.assertIn('Yeni Çiftlik',body.decode())
  staff_token=self.csrf('farm-staff');self.request('/farms/create?farm=primary',{'name':'Staff','csrf':staff_token},sid='farm-staff')
  self.assertEqual(len(self.registry.farms()),2)
  status,headers,_=self.request('/farms/switch?farm='+target,{'target':'primary','csrf':token});self.assertEqual(status,303);self.assertIn('farm=primary',headers['Location'])
 def test_staff_grant_revoke_enforced_on_pages_photos_and_actions(self):
  farm=self.create();fid=farm['id'];self.seed(farm,'SECOND-ANIMAL')
  self.assertEqual(self.request('/all-animals?farm='+fid,sid='farm-staff')[0],403)
  token=self.csrf();self.request('/farms/access?farm=primary',{'csrf':token,'username':'staff','access_'+fid:'1'})
  status,_,body=self.request('/all-animals?farm='+fid,sid='farm-staff');self.assertEqual(status,200);self.assertIn('SECOND-ANIMAL',body.decode())
  self.request('/farms/access?farm=primary',{'csrf':token,'username':'staff'})
  self.assertEqual(self.request('/photo-preview?name=x.jpg&farm='+fid,sid='farm-staff')[0],403)
  self.assertEqual(self.request('/farm-profile?farm='+fid,{'farm_name':'bad'},sid='farm-staff')[0],403)
 def test_concurrent_gets_and_old_tab_post_use_explicit_farm(self):
  a=self.create('Çiftlik A');b=self.create('Çiftlik B');self.seed(a,'ONLY-A');self.seed(b,'ONLY-B');server.SESSIONS['farm-admin']['active_farm']=b['id']
  def read(i):
   farm,yes,no=(a,'ONLY-A','ONLY-B') if i%2 else (b,'ONLY-B','ONLY-A')
   status,_,body=self.request('/all-animals?farm='+farm['id']);text=body.decode();return status==200 and yes in text and no not in text and 'FIRST-ANIMAL' not in text
  with ThreadPoolExecutor(max_workers=6) as pool:self.assertTrue(all(pool.map(read,range(18))))
  self.request('/farm-profile?farm='+a['id'],{'farm_name':'A Güncellendi'})
  with farms.scope(a):self.assertEqual(server.setting_get('farm_name'),'A Güncellendi')
  with farms.scope(b):self.assertEqual(server.setting_get('farm_name'),'Çiftlik B')
  self.assertEqual(farms.current_id(),'primary')
 def test_same_photo_name_isolated_and_anonymous_denied(self):
  a=self.create('A');b=self.create('B');values=[]
  for farm,color in [(a,'red'),(b,'blue')]:
   with farms.scope(farm):Image.new('RGB',(900,600),color).save(Path(server.UPLOADS)/'same.jpg')
   status,_,body=self.request('/photo-preview?name=same.jpg&size=320&farm='+farm['id']);self.assertEqual(status,200)
   with Image.open(io.BytesIO(body)) as image:values.append(image.getpixel((0,0)))
   self.assertEqual(self.request('/uploads/same.jpg?farm='+farm['id'],sid='')[0],401)
  self.assertNotEqual(values[0],values[1])
 def test_navigation_forms_assets_and_referer_binding(self):
  farm=self.create();self.seed(farm,'SECOND')
  text=self.request('/animal?id=1&farm='+farm['id'])[2].decode();self.assertIn('cpEnterpriseConfig',text);self.assertIn('farms.js?v='+release_info.VERSION,text);self.assertIn('Aktif işletme',text)
  workbench=self.request('/ration-workbench?id=1&farm='+farm['id'])[2].decode();self.assertIn('formaction="/ration/recalculate?farm='+farm['id']+'"',workbench)
  status,headers,_=self.request('/all-animals',headers={'Referer':self.base+'/?farm='+farm['id']});self.assertEqual(status,303);self.assertIn('farm='+farm['id'],headers['Location'])
 def test_backup_separate_and_cross_restore_rejected(self):
  farm=self.create();self.seed(farm,'SECOND');name=server.create_backup('test');primary=server.configured_backup_dir()/name
  with farms.scope(farm):
   name=server.create_backup('test');path=server.configured_backup_dir()/name;self.assertNotEqual(path.parent,primary.parent)
   with zipfile.ZipFile(path) as z:self.assertEqual(json.loads(z.read('manifest.json'))['farm_id'],farm['id'])
   self.assertFalse(server.validate_backup_zip(primary)[0])
   with self.assertRaises(ValueError):server.restore_backup_zip(primary)
   self.assertTrue(server.validate_backup_zip(path)[0]);server.restore_backup_zip(path)
   with server.db() as c:self.assertEqual(c.execute('select tag from animals').fetchone()[0],'SECOND')
 def test_shared_credentials_and_inactive_sessions(self):
  farm=self.create()
  with server.db() as c:c.execute("update users set password=?,full_name='Yeni İsim' where username='staff'",(server.password_hash('new-password-123'),))
  self.registry.sync_accounts(farm)
  with farms.scope(farm):
   with server.db() as c:row=c.execute("select password,full_name from users where username='staff'").fetchone()
   self.assertTrue(server.password_verify('new-password-123',row['password']));self.assertEqual(row['full_name'],'Yeni İsim')
  with server.db() as c:c.execute("update users set active=0 where username='staff'")
  self.assertIn(self.request('/all-animals?farm=primary',sid='farm-staff')[0],(303,401))
 def test_preview_partition_and_context_cleanup(self):
  a=self.create('A');b=self.create('B')
  with farms.scope(a):server.ANIMAL_IMPORT_PREVIEWS['same']={'farm':'a'}
  with farms.scope(b):self.assertIsNone(server.ANIMAL_IMPORT_PREVIEWS.get('same'))
  self.assertIsNone(server.ANIMAL_IMPORT_PREVIEWS.get('same'));self.assertEqual(self.request('/all-animals?farm=../../bad')[0],404)
  with self.assertRaises(RuntimeError):
   with farms.scope(a):raise RuntimeError('cleanup')
  self.assertEqual(farms.current_id(),'primary')
 def test_api_membership_and_token_scope(self):
  farm=self.create();fid=farm['id']
  def login(username,password,fid):
   req=urllib.request.Request(self.base+'/api/v1/login?farm='+fid,data=json.dumps({'username':username,'password':password}).encode(),headers={'Content-Type':'application/json'})
   try:
    with urllib.request.urlopen(req) as r:return r.status,json.load(r)
   except urllib.error.HTTPError as r:return r.code,json.load(r)
  self.assertEqual(login('staff','test-staff-123',fid)[0],403)
  status,body=login('admin','test-admin-123',fid);self.assertEqual(status,200);token=body['token']
  self.assertEqual(self.request('/api/v1/me?farm='+fid,sid='',headers={'Authorization':'Bearer '+token})[0],200)
  self.assertEqual(self.request('/api/v1/me?farm=primary',sid='',headers={'Authorization':'Bearer '+token})[0],401)
 def test_finance_post_stock_ration_and_settings_stay_separate(self):
  a=self.create('A');b=self.create('B')
  server.SESSIONS['farm-admin']['active_farm']=b['id']
  payload={'tx_date':server.date.today().isoformat(),'tx_type':'Gider','category':'Diğer','amount':'123.45','description':'ONLY-A-EXPENSE','payment_method':'Nakit'}
  self.assertEqual(self.request('/finance?farm='+a['id'],payload)[0],303)
  with farms.scope(a):
   with server.db() as c:
    self.assertEqual(c.execute("select amount from finance where description='ONLY-A-EXPENSE'").fetchone()[0],123.45)
    c.execute("update rations set name='A-RATION' where id=(select min(id) from rations)")
    c.execute("update feed_catalog set name='A-FEED' where id=(select min(id) from feed_catalog)")
   server.setting_set('backup_directory','')
  with farms.scope(b):
   with server.db() as c:
    self.assertIsNone(c.execute("select id from finance where description='ONLY-A-EXPENSE'").fetchone())
    self.assertIsNone(c.execute("select id from rations where name='A-RATION'").fetchone())
    self.assertIsNone(c.execute("select id from feed_catalog where name='A-FEED'").fetchone())
  with server.db() as c:self.assertIsNone(c.execute("select id from finance where description='ONLY-A-EXPENSE'").fetchone())
 def test_registry_reopen_startup_migration_and_all_business_daily_backups(self):
  a=self.create('A');self.seed(a,'RESTART-ANIMAL')
  reopened=farms.Registry(vars(server));self.assertEqual(reopened.farm(a['id'])['name'],'A')
  server.init_db()
  with farms.scope(reopened.farm(a['id'])):
   with server.db() as c:self.assertEqual(c.execute('select tag from animals').fetchone()[0],'RESTART-ANIMAL')
  server.daily_backup()
  for farm in reopened.farms():
   with farms.scope(farm):self.assertTrue(list(server.configured_backup_dir().glob('CiftlikPro_Backup_otomatik_*.zip')))
 def test_shared_custom_backup_directory_is_partitioned(self):
  a=self.create('A');b=self.create('B');base=self.root/'common-backups'
  for farm in (a,b):
   with farms.scope(farm):
    server.setting_set('backup_directory',str(base));path=server.configured_backup_dir()
    self.assertEqual(path,base/('isletme-'+farm['id']))

 def test_json_export_identity_and_tagged_cross_import_rejected(self):
  a=self.create('A');self.seed(a,'ONLY-A')
  with farms.scope(a):payload=server.export_payload()
  self.assertEqual(payload['farm_id'],a['id'])
  with self.assertRaises(ValueError):server.import_payload(payload)
  with server.db() as c:self.assertIsNone(c.execute("select id from animals where tag='ONLY-A'").fetchone())

 def test_tape_estimate_keeps_scale_weights_and_farms_separate(self):
  farm=self.create('Besi');fid=farm['id'];self.seed(farm,'BRANGUS')
  today=server.date.today().isoformat()
  with farms.scope(farm),server.db() as c:
   aid=c.execute("select id from animals where tag='BRANGUS'").fetchone()[0]
   previous=(server.date.today()-server.timedelta(days=20)).isoformat()
   c.executemany('insert into weights(animal_id,measure_date,weight) values(?,?,?)',[(aid,today,300),(aid,previous,280)])
  server.SESSIONS['farm-admin']['active_farm']='primary'
  card=self.request(f'/animal?id={aid}&farm={fid}',headers={'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X)'})
  self.assertEqual(card[0],200);self.assertIn('Tahmini Ağırlık',card[2].decode())
  token=server.SESSIONS['farm-admin']['farm_csrf']
  action=f'/animal/estimate-weight?farm={fid}'
  fields={'animal_id':aid,'csrf':token,'measure_date':today,'girth_cm':'160,5','length_cm':'130','notes':'<b>Test</b>'}
  self.assertEqual(self.request(action,dict(fields,csrf='bad'))[0],403)
  self.assertIn('geçersiz',urllib.parse.unquote_plus(self.request(action,dict(fields,measure_date='bad'))[1]['Location']))
  self.assertIn('ileri tarih',urllib.parse.unquote_plus(self.request(action,dict(fields,measure_date='9999-01-01'))[1]['Location']))
  self.assertIn('santimetre',urllib.parse.unquote_plus(self.request(action,dict(fields,girth_cm='NaN'))[1]['Location']))
  with farms.scope(farm),server.db() as c:
   self.assertEqual(c.execute('select count(*) from weight_estimates').fetchone()[0],0)
  status,headers,_=self.request(action,fields)
  self.assertEqual(status,303);self.assertTrue(headers['Location'].endswith('#growth'))
  with farms.scope(farm),server.db() as c:
   row=c.execute('select * from weight_estimates').fetchone()
   self.assertEqual((row['animal_id'],row['girth_cm'],row['estimated_kg']),(aid,160.5,309.0))
   self.assertEqual(c.execute('select weight from weights order by measure_date desc').fetchone()[0],300)
   self.assertEqual(server.male_weight_performance(aid,c)['daily'],1.0)
  with server.db() as c:self.assertEqual(c.execute('select count(*) from weight_estimates').fetchone()[0],0)
  html=self.request(f'/animal?id={aid}&farm={fid}')[2].decode()
  self.assertIn('≈ 309,0 kg',html);self.assertIn('&lt;b&gt;Test&lt;/b&gt;',html)
  self.assertEqual(self.request(action,dict(fields,girth_cm='162'))[0],303)
  with farms.scope(farm),server.db() as c:
   estimates=c.execute('select id,girth_cm from weight_estimates').fetchall()
   self.assertEqual([tuple(x) for x in estimates],[(row['id'],162)])
  self.assertEqual(self.request(f'/animal/estimate-weight/delete?farm={fid}',{'animal_id':aid,'estimate_id':row['id'],'csrf':token})[0],303)
  with farms.scope(farm),server.db() as c:
   self.assertEqual(c.execute('select count(*) from weight_estimates').fetchone()[0],0)
   self.assertEqual(c.execute('select weight from weights order by measure_date desc').fetchone()[0],300)
