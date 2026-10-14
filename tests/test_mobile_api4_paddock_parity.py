import os,sys,tempfile,importlib.util,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; APP=ROOT/'app'
if str(APP) not in sys.path: sys.path.insert(0,str(APP))
class PaddockParityTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); os.environ['CIFTLIKPRO_DATA_DIR']=self.tmp.name; os.environ['CIFTLIKPRO_TEST_AUTOCLOSE_DB']='1'
  spec=importlib.util.spec_from_file_location('server_mobile_api4_test',APP/'server.py'); self.s=importlib.util.module_from_spec(spec); spec.loader.exec_module(self.s); self.s.init_db()
 def tearDown(self): self.tmp.cleanup()
 def test_population_matches_desktop_definition(self):
  with self.s.db() as c:
   c.execute("insert into paddocks(name,active,created_at) values('SO3',1,'2026-10-13T10:00:00')"); pid=c.execute("select id from paddocks where name='SO3'").fetchone()['id']
   c.execute("insert into animals(tag,gender,status,paddock_id) values('A1','Dişi','Aktif',?)",(pid,))
   mother=c.execute("select id from animals where tag='A1'").fetchone()['id']; c.execute("insert into calves(mother_id,tag,gender,birth_date,status,paddock_id) values(?,'C1','Dişi','2026-01-01','Aktif',?)",(mother,pid))
   self.assertEqual(self.s.paddock_population(pid,c),2)
 def test_mobile_paddock_api_uses_shared_population(self):
  text=(APP/'server.py').read_text(encoding='utf-8')
  self.assertIn("item['animal_count']=paddock_population(int(row['id']),con)",text)
  self.assertIn("from calves ca left join paddocks",text)
  self.assertIn("not exists(select 1 from animal_losses l where l.calf_id=ca.id)",text)
if __name__=='__main__': unittest.main()
