import sys
import time
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'app'))
import server


class Hotfix122BHTests(unittest.TestCase):
    def test_birth_closed_record_is_absent_from_shared_active_count(self):
        server.init_db()
        stamp=str(time.time_ns())[-12:]
        animal_id=calf_id=insemination_id=None
        try:
            with server.db() as con:
                animal_id=con.execute(
                    "insert into animals(tag,gender,status) values(?,'Dişi','Aktif')",
                    ('TRBH'+stamp,)
                ).lastrowid
                insemination_id=con.execute(
                    "insert into inseminations(animal_id,attempt,insemination_date,pregnancy_result,due_date) values(?,?,?,?,?)",
                    (animal_id,1,'2026-01-01','Pozitif','2026-10-08')
                ).lastrowid
                self.assertIn(animal_id,server.active_pregnancy_records(con))
                calf_id=con.execute(
                    "insert into calves(tag,mother_id,birth_date,gender,status) values(?,?,?,'Dişi','Aktif')",
                    ('TRBHC'+stamp,animal_id,'2026-10-05')
                ).lastrowid
                server.reconcile_birth_closed_pregnancies(con)
                self.assertNotIn(animal_id,server.active_pregnancy_records(con))
                self.assertEqual(
                    con.execute('select pregnancy_result from inseminations where id=?',(insemination_id,)).fetchone()[0],
                    'Doğum'
                )
                self.assertEqual(server.pregnancy_vaccine_tasks(con,animal_id=animal_id,horizon_days=365),[])
        finally:
            with server.db() as con:
                if calf_id:con.execute('delete from calves where id=?',(calf_id,))
                if insemination_id:con.execute('delete from inseminations where id=?',(insemination_id,))
                if animal_id:con.execute('delete from animals where id=?',(animal_id,))

    def test_release_version_is_122bh(self):
        self.assertEqual(server.APP_VERSION,'3.9.23 DEV4 Hotfix1.22bq')
        self.assertEqual(server.APP_LABEL,'v3.9.23 DEV4 Hotfix1.22bq')


if __name__=='__main__':
    unittest.main()
