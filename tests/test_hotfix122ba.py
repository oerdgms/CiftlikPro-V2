import sys,time,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
import server

class Hotfix122BATests(unittest.TestCase):
    def test_birth_closes_active_pregnancy(self):
        server.init_db()
        stamp=str(time.time_ns())
        tag='TRBA'+stamp[-10:]
        calf_tag='TRBC'+stamp[-10:]
        aid=None;cid=None;iid=None
        try:
            with server.db() as c:
                aid=c.execute("insert into animals(tag,gender,status) values(?,'Dişi','Aktif')",(tag,)).lastrowid
                iid=c.execute("insert into inseminations(animal_id,attempt,insemination_date,pregnancy_result,due_date) values(?,?,?,?,?)",(aid,1,'2026-01-01','Pozitif','2026-10-08')).lastrowid
                self.assertIsNotNone(server.current_pregnancy_record(c,aid))
                cid=c.execute("insert into calves(tag,mother_id,birth_date,gender,status) values(?,?,?,'Dişi','Aktif')",(calf_tag,aid,'2026-10-05')).lastrowid
                server.close_pregnancy_after_birth(c,aid,'2026-10-05')
                result=c.execute('select pregnancy_result from inseminations where id=?',(iid,)).fetchone()['pregnancy_result']
                self.assertEqual(result,'Doğum')
                self.assertIsNone(server.current_pregnancy_record(c,aid))
        finally:
            with server.db() as c:
                if cid:c.execute('delete from calves where id=?',(cid,))
                if iid:c.execute('delete from inseminations where id=?',(iid,))
                if aid:c.execute('delete from animals where id=?',(aid,))

    def test_dashboard_critical_stock_excludes_zero(self):
        source=Path(server.__file__).read_text(encoding='utf-8')
        self.assertIn("low_feed_rows=[r for r in low_feed_candidates if float(r['stock'] or 0)>0][:5]",source)
        self.assertEqual(server.APP_VERSION,'3.9.23 DEV4 Hotfix1.22bd')

if __name__=='__main__':unittest.main()
