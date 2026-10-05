import sys
import time
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'app'))
import server


class Hotfix122BGTests(unittest.TestCase):
    def test_existing_birth_closes_stale_positive_pregnancy_idempotently(self):
        server.init_db()
        stamp=str(time.time_ns())[-12:]
        animal_id=calf_id=insemination_id=None
        try:
            with server.db() as con:
                animal_id=con.execute(
                    "insert into animals(tag,gender,status) values(?,'Dişi','Aktif')",
                    ('TRBG'+stamp,)
                ).lastrowid
                insemination_id=con.execute(
                    "insert into inseminations(animal_id,attempt,insemination_date,pregnancy_result,due_date) values(?,?,?,?,?)",
                    (animal_id,1,'2026-01-01','Pozitif','2026-10-08')
                ).lastrowid
                calf_id=con.execute(
                    "insert into calves(tag,mother_id,birth_date,gender,status) values(?,?,?,'Dişi','Aktif')",
                    ('TRBC'+stamp,animal_id,'2026-10-05')
                ).lastrowid
                self.assertEqual(server.reconcile_birth_closed_pregnancies(con),1)
                self.assertEqual(
                    con.execute('select pregnancy_result from inseminations where id=?',(insemination_id,)).fetchone()[0],
                    'Doğum'
                )
                self.assertEqual(server.reconcile_birth_closed_pregnancies(con),0)
                self.assertIsNone(server.current_pregnancy_record(con,animal_id))
        finally:
            with server.db() as con:
                if calf_id:con.execute('delete from calves where id=?',(calf_id,))
                if insemination_id:con.execute('delete from inseminations where id=?',(insemination_id,))
                if animal_id:con.execute('delete from animals where id=?',(animal_id,))

    def test_card_status_does_not_fall_back_to_stale_positive(self):
        latest={'pregnancy_result':'Pozitif'}
        self.assertEqual(server.pregnancy_display_status(latest,None),'Doğum')
        active={'pregnancy_result':'Pozitif'}
        self.assertEqual(server.pregnancy_display_status(latest,active),'Pozitif')
        self.assertEqual(server.pregnancy_display_status({'pregnancy_result':'Negatif'},None),'Negatif')

    def test_release_version_is_122bg(self):
        self.assertEqual(server.APP_VERSION,'3.9.23 DEV4 Hotfix1.22bh')
        self.assertEqual(server.APP_LABEL,'v3.9.23 DEV4 Hotfix1.22bh')


if __name__=='__main__':
    unittest.main()
