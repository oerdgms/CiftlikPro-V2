"""Context and read-only guarantees for the shared animal event chooser."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_reports_import import server
import animal_actions as actions


class AnimalActionsTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.patch=patch.object(server,'DB',Path(self.temp.name)/'events.db');self.patch.start()
        server.init_db();self.today=server.date.today().isoformat()
        with server.db() as c:
            self.female=c.execute("insert into animals(tag,nickname,gender,status,breed) values('EVENT-F',?,'Dişi','Aktif','Simental')",('<script>alert(1)</script>',)).lastrowid
            self.male=c.execute("insert into animals(tag,gender,status) values('EVENT-M','Erkek','Aktif')").lastrowid
            self.calf=c.execute("insert into calves(tag,mother_id,gender,status,birth_date) values('EVENT-C',?,'Dişi','Aktif',?)",(self.female,self.today)).lastrowid

    def tearDown(self):
        self.patch.stop();self.temp.cleanup()

    def markup(self,event='',source='animal',sid=None):
        return actions.markup(vars(server),{'source':[source],'id':[str(sid or self.female)],'event':[event]})

    def test_only_adult_females_get_reproduction_and_dairy_actions(self):
        self.assertIn('Doğum Yaptı',self.markup())
        self.assertIn('Sağmal / Laktasyonda',self.markup())
        for source,sid in [('animal',self.male),('calf',self.calf)]:
            text=self.markup(source=source,sid=sid)
            self.assertIn('Sağlık Kaydı',text);self.assertIn('Kilo Ölçümü',text)
            self.assertNotIn('Doğum Yaptı',text);self.assertNotIn('Gebe Değil',text)
            with self.assertRaises(ValueError):self.markup('dry',source,sid)

    def test_inactive_promoted_and_invalid_subjects_cannot_open_forms(self):
        with server.db() as c:
            c.execute("update animals set status='Satıldı' where id=?",(self.male,))
            c.execute('update calves set promoted_animal_id=? where id=?',(self.female,self.calf))
        for source,sid in [('animal',self.male),('calf',self.calf),('animal',-1),('animal','1 OR 1=1'),('animal',2**63),('other',self.female)]:
            with self.subTest(source=source,sid=sid):
                with self.assertRaises(ValueError):self.markup(source=source,sid=sid)

    def test_chooser_and_forms_do_not_create_records_or_fake_insemination_dates(self):
        with server.db() as c:
            before={table:c.execute('select count(*) from '+table).fetchone()[0] for table in ('animals','calves','inseminations','animal_dairy_status','animal_dairy_status_history','milk','finance')}
        for event in ('','heat','inseminated','dry','heifer','lactating','birth','weight','pregnant','empty'):
            self.markup(event)
        self.assertNotIn('action="/reproduction-status"',self.markup('pregnant'))
        with server.db() as c:
            after={table:c.execute('select count(*) from '+table).fetchone()[0] for table in before}
        self.assertEqual(after,before)

    def test_pregnancy_form_targets_latest_open_record_and_closed_birth_is_not_reopened(self):
        with server.db() as c:
            c.execute("insert into inseminations(animal_id,attempt,insemination_date,pregnancy_result) values(?,1,'2026-01-01','Negatif')",(self.female,))
            latest=c.execute("insert into inseminations(animal_id,attempt,insemination_date,pregnancy_result) values(?,2,?,'Bekleniyor')",(self.female,self.today)).lastrowid
        text=self.markup('pregnant')
        self.assertIn(f'name="id" value="{latest}"',text)
        self.assertIn('name="pregnancy_result" value="Pozitif"',text)
        with server.db() as c:c.execute("update inseminations set pregnancy_result='Doğum' where id=?",(latest,))
        self.assertNotIn('action="/reproduction-status"',self.markup('pregnant'))

    def test_birth_and_weight_keep_correct_subject_and_escape_user_text(self):
        text=self.markup('birth')
        self.assertIn(f'name="mother_id" value="{self.female}"',text)
        self.assertIn('name="arrival_source" value="Çiftlikte Doğdu"',text)
        self.assertIn('action="/animal-add"',text)
        self.assertNotIn('<script>alert(1)</script>',text)
        self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;',text)
        text=self.markup('weight','calf',self.calf)
        self.assertIn('action="/calf/weight"',text)
        self.assertIn(f'name="calf_id" value="{self.calf}"',text)


if __name__=='__main__':unittest.main()
