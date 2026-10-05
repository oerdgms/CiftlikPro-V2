import sys
import time
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'app'))
import server


class Hotfix122BETests(unittest.TestCase):
    def test_dashboard_counts_birth_and_mother_paddock_stay_consistent(self):
        server.init_db()
        stamp=str(time.time_ns())[-12:]
        mother_tag='TRBE'+stamp
        calf_tag='TRBF'+stamp
        paddock_id=mother_id=calf_id=insemination_id=None
        try:
            with server.db() as con:
                paddock_id=con.execute(
                    "insert into paddocks(name,code,type,active,created_at) values(?,?,?,?,?)",
                    ('BE Padok '+stamp,'BE'+stamp[-4:],'Doğum',1,'2026-10-05T00:00:00')
                ).lastrowid
                mother_id=con.execute(
                    "insert into animals(tag,gender,status,paddock,paddock_id) values(?,'Dişi','Aktif',?,?)",
                    (mother_tag,'BE Padok '+stamp,paddock_id)
                ).lastrowid
                before=server.dashboard_herd_counts(con)
                insemination_id=con.execute(
                    "insert into inseminations(animal_id,attempt,insemination_date,pregnancy_result,due_date) values(?,?,?,?,?)",
                    (mother_id,1,'2026-01-01','Pozitif','2026-10-08')
                ).lastrowid
                mother=con.execute('select id,tag,paddock,paddock_id from animals where id=?',(mother_id,)).fetchone()
                inherited_id,inherited_name=server.resolve_entry_paddock(con,None,mother,True)
                self.assertEqual(inherited_id,paddock_id)
                self.assertEqual(inherited_name,'BE Padok '+stamp)
                calf_id=con.execute(
                    """insert into calves(tag,mother_id,birth_date,gender,status,paddock,paddock_id,arrival_source,entry_date)
                       values(?,?,?,'Dişi','Aktif',?,?,?,?)""",
                    (calf_tag,mother_id,'2026-10-05',inherited_name,inherited_id,'Çiftlikte Doğdu','2026-10-05')
                ).lastrowid
                server.close_pregnancy_after_birth(con,mother_id,'2026-10-05')
                after=server.dashboard_herd_counts(con)
                self.assertEqual(after['calf'],before['calf']+1)
                self.assertEqual(after['total'],before['total']+1)
                self.assertIsNone(server.current_pregnancy_record(con,mother_id))
                self.assertEqual(con.execute('select pregnancy_result from inseminations where id=?',(insemination_id,)).fetchone()[0],'Doğum')
        finally:
            with server.db() as con:
                if calf_id:con.execute('delete from calves where id=?',(calf_id,))
                if insemination_id:con.execute('delete from inseminations where id=?',(insemination_id,))
                if mother_id:con.execute('delete from animals where id=?',(mother_id,))
                if paddock_id:con.execute('delete from paddocks where id=?',(paddock_id,))

    def test_smart_form_and_detail_language_include_newborn_guards(self):
        html=server.render_smart_animal_add(
            [{'id':7,'tag':'TR580000007','nickname':'Anne','paddock_id':3,'paddock':'Doğum'}],
            ['Simental'],[{'id':3,'name':'Doğum','code':'D01'}]
        )
        self.assertIn('data-paddock="3"',html)
        self.assertIn('id="paddockId"',html)
        self.assertIn('syncBornPaddock',html)
        source=(ROOT/'app'/'server.py').read_text(encoding='utf-8')
        self.assertIn("initial_cost_label='Başlangıç Maliyeti'",source)
        self.assertIn('İşletmede doğdu:',source)

    def test_mobile_reproduction_fix_and_release_names_are_packaged(self):
        dashboard=server.page('Dashboard','<div class="v117-dashboard"></div>','/','admin')
        reproduction=server.page('Üreme','<div class="repro-board-compact"></div>','/reproduction-center','admin')
        self.assertIn('hotfix122be-completion',dashboard)
        self.assertNotIn('body.v118-shell .v117-dashboard>.v122au-task-panel{grid-row:auto',dashboard)
        self.assertIn('scroll-margin-top:144px',reproduction)
        self.assertEqual(server.APP_VERSION,'3.9.23 DEV4 Hotfix1.22bh')
        installer=(ROOT/'installer.iss').read_text(encoding='utf-8')
        workflow=(ROOT/'.github'/'workflows'/'windows-installer.yml').read_text(encoding='utf-8')
        expected='CiftlikPro_Enterprise_V3_9_23_DEV4_Hotfix1_22bh_Setup.exe'
        self.assertIn('OutputBaseFilename='+expected[:-4],installer)
        self.assertIn(expected,workflow)


if __name__=='__main__':
    unittest.main()
