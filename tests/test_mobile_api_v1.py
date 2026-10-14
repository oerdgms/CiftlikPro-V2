import os, sys, tempfile, importlib.util, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
APP=ROOT/'app'
if str(APP) not in sys.path:sys.path.insert(0,str(APP))

class MobileApiV1Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();os.environ['CIFTLIKPRO_DATA_DIR']=self.tmp.name;os.environ['CIFTLIKPRO_TEST_AUTOCLOSE_DB']='1'
        spec=importlib.util.spec_from_file_location('server_mobile_api_test',APP/'server.py');self.s=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.s);self.s.init_db()
    def tearDown(self):self.tmp.cleanup()
    def test_mobile_token_table_exists(self):
        with self.s.db() as c:
            names={r[0] for r in c.execute("select name from sqlite_master where type='table'").fetchall()}
        self.assertIn('mobile_api_tokens',names)
    def test_api_animal_summary_uses_same_db(self):
        with self.s.db() as c:
            c.execute("insert into animals(tag,nickname,gender,breed,birth_date,status) values('TRM001','Mobil','Erkek','Simental','2025-01-01','Aktif')")
            r=c.execute("select a.*,coalesce(p.name,a.paddock,'') paddock_name from animals a left join paddocks p on p.id=a.paddock_id where a.tag='TRM001'").fetchone();d=self.s._api_animal_summary(c,r)
        self.assertEqual(d['tag'],'TRM001');self.assertEqual(d['status'],'Aktif');self.assertFalse(d['pregnant'])
    def test_token_hash_is_not_plain_token(self):
        token='ornek-gizli-token';self.assertNotEqual(self.s._api_token_hash(token),token);self.assertEqual(len(self.s._api_token_hash(token)),64)

if __name__=='__main__':unittest.main()
