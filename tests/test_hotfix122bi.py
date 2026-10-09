import threading
import time
import unittest
import urllib.parse
import urllib.request
from datetime import date, timedelta
from unittest.mock import patch

from test_reports_import import server


class Hotfix122BITests(unittest.TestCase):
    def setUp(self):
        server.init_db()
        stamp=str(time.time_ns())[-12:]
        self.ids=[]
        self.insemination_ids=[]
        with server.db() as con:
            for suffix,result,days in (
                ('C','Bekleniyor',30),
                ('P','Pozitif',70),
                ('N','Negatif',42),
            ):
                animal_id=con.execute(
                    "insert into animals(tag,nickname,gender,status,paddock) values(?,?,'Dişi','Aktif','BI01')",
                    ('TRBI'+suffix+stamp,'Test '+suffix),
                ).lastrowid
                ins_day=date.today()-timedelta(days=days)
                due=(ins_day+timedelta(days=280)).isoformat() if result=='Pozitif' else ''
                insemination_id=con.execute(
                    'insert into inseminations(animal_id,attempt,insemination_date,pregnancy_result,due_date) values(?,?,?,?,?)',
                    (animal_id,1,ins_day.isoformat(),result,due),
                ).lastrowid
                self.ids.append(animal_id)
                self.insemination_ids.append(insemination_id)

    def tearDown(self):
        with server.db() as con:
            if self.insemination_ids:
                con.execute(
                    'delete from inseminations where id in (%s)' % ','.join('?'*len(self.insemination_ids)),
                    self.insemination_ids,
                )
            if self.ids:
                con.execute(
                    'delete from animals where id in (%s)' % ','.join('?'*len(self.ids)),
                    self.ids,
                )

    def test_quick_result_updates_only_latest_record_and_due_date(self):
        animal_id=self.ids[0]
        latest_id=self.insemination_ids[0]
        with server.db() as con:
            older_id=con.execute(
                "insert into inseminations(animal_id,attempt,insemination_date,pregnancy_result,due_date) values(?,2,?,'Negatif','')",
                (animal_id,(date.today()-timedelta(days=100)).isoformat()),
            ).lastrowid
            self.insemination_ids.append(older_id)
            with self.assertRaisesRegex(ValueError,'en güncel'):
                server.set_latest_pregnancy_result(con,older_id,'Pozitif')

            rec,stored,due=server.set_latest_pregnancy_result(con,latest_id,'Pozitif')
            self.assertEqual(rec['animal_id'],animal_id)
            self.assertEqual(stored,'Pozitif')
            expected=(date.fromisoformat(rec['insemination_date'])+timedelta(days=280)).isoformat()
            self.assertEqual(due,expected)
            self.assertIsNotNone(server.current_pregnancy_record(con,animal_id))

            _,stored,due=server.set_latest_pregnancy_result(con,latest_id,'Negatif')
            self.assertEqual((stored,due),('Negatif',''))
            self.assertIsNone(server.current_pregnancy_record(con,animal_id))

    def test_reproduction_filters_and_quick_dialog_are_rendered(self):
        server.SESSIONS['hotfix122bi']={'username':'admin','role':'admin'}
        http=server.QuietThreadingHTTPServer(('127.0.0.1',0),server.App)
        threading.Thread(target=http.serve_forever,daemon=True).start()
        try:
            with patch.object(server,'license_status',return_value=(True,{},'')):
                request=urllib.request.Request(
                    f'http://127.0.0.1:{http.server_port}/reproduction-center?stage=negative',
                    headers={'Cookie':'sid=hotfix122bi'},
                )
                with urllib.request.urlopen(request,timeout=20) as response:
                    html=response.read().decode()
            for marker in (
                'data-repro-filter="control"',
                'data-repro-filter="pregnant"',
                'data-repro-filter="negative"',
                'data-repro-section="negative"',
                'id="reproStatusDialog"',
                'action="/reproduction-status"',
                'name="pregnancy_result" id="reproStatusResult"',
                'hotfix122bi-reproduction-filter-status',
                '.repro-board-compact .repro-column[hidden]',
                "validStages=new Set(['all','estrus','inseminated','control','pregnant','negative','birth','uncertain','empty',...lifeStages])",
            ):
                self.assertIn(marker,html)
            self.assertIn('Gebelik Kontrolü',html)
            self.assertIn('Gebe Değil',html)
            self.assertIn('Sonucu Güncelle',html)
            self.assertIn('Kontrol Sonucu',html)
        finally:
            http.shutdown()
            http.server_close()
            server.SESSIONS.pop('hotfix122bi',None)

    def test_quick_result_post_updates_and_returns_to_selected_filter(self):
        server.SESSIONS['hotfix122bi-post']={'username':'admin','role':'admin'}
        http=server.QuietThreadingHTTPServer(('127.0.0.1',0),server.App)
        threading.Thread(target=http.serve_forever,daemon=True).start()
        try:
            payload=urllib.parse.urlencode({
                'id':self.insemination_ids[0],
                'pregnancy_result':'Pozitif',
                'return_to':f'/reproduction-center?stage=pregnant&animal={self.ids[0]}',
            }).encode()
            request=urllib.request.Request(
                f'http://127.0.0.1:{http.server_port}/reproduction-status',
                data=payload,
                method='POST',
                headers={'Cookie':'sid=hotfix122bi-post','Content-Type':'application/x-www-form-urlencoded'},
            )
            with patch.object(server,'license_status',return_value=(True,{},'')):
                with urllib.request.urlopen(request,timeout=20) as response:
                    html=response.read().decode()
                    self.assertIn('stage=pregnant',response.geturl())
            self.assertIn('gebelik sonucu: Gebe',html)
            with server.db() as con:
                row=con.execute('select pregnancy_result,due_date from inseminations where id=?',(self.insemination_ids[0],)).fetchone()
            self.assertEqual(row['pregnancy_result'],'Pozitif')
            self.assertTrue(row['due_date'])
        finally:
            http.shutdown()
            http.server_close()
            server.SESSIONS.pop('hotfix122bi-post',None)

    def test_release_version_is_122bi(self):
        self.assertEqual(server.APP_VERSION,'3.9.23 DEV4 Hotfix1.22cd')
        self.assertEqual(server.APP_LABEL,'v3.9.23 DEV4 Hotfix1.22cd')


if __name__=='__main__':
    unittest.main()
