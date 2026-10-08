import re
import tempfile
import threading
import unittest
import urllib.request
from pathlib import Path
from datetime import date, timedelta
from unittest.mock import patch
from test_reports_import import server


class ReproductionPopulationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.db_patch=patch.object(server,'DB',Path(self.temp.name)/'test.db')
        self.db_patch.start()
        server.init_db()
        self.groups={name:[] for name in ('pregnant','negative','control','empty')}
        self.ins={}
        with server.db() as con:
            for name,count,result in [('pregnant',21,'Pozitif'),('negative',3,'Negatif'),('control',2,'Bekleniyor'),('empty',6,None)]:
                for n in range(count):
                    aid=con.execute("insert into animals(tag,gender,status,paddock) values(?,'Dişi','Aktif',?)",(f'BK-{name}-{n}','BK-A' if n%2==0 else 'BK-B')).lastrowid
                    self.groups[name].append(aid)
                    if result:
                        day=date.today()-timedelta(days=250 if name=='pregnant' and n<2 else 40)
                        iid=con.execute('insert into inseminations(animal_id,attempt,insemination_date,pregnancy_result,due_date) values(?,1,?,?,?)',(aid,day.isoformat(),result,(day+timedelta(days=280)).isoformat() if result=='Pozitif' else '')).lastrowid
                        self.ins[aid]=iid
            con.execute("insert into animals(tag,gender,status) values('BK-male','Erkek','Aktif')")
            con.execute("insert into animals(tag,gender,status) values('BK-sold','Dişi','Satıldı')")
        server.SESSIONS['bk-test']={'username':'admin','role':'admin'}
        self.http=server.QuietThreadingHTTPServer(('127.0.0.1',0),server.App)
        threading.Thread(target=self.http.serve_forever,daemon=True).start()

    def tearDown(self):
        self.http.shutdown();self.http.server_close()
        server.SESSIONS.pop('bk-test',None)
        self.db_patch.stop();self.temp.cleanup()

    def render(self):
        req=urllib.request.Request(f'http://127.0.0.1:{self.http.server_port}/reproduction-center',headers={'Cookie':'sid=bk-test'})
        with patch.object(server,'license_status',return_value=(True,{},'')):
            with urllib.request.urlopen(req,timeout=20) as response:
                return response.read().decode()

    def ids(self,html,stage):
        part=html.split(f'data-repro-section="{stage}"',1)[1].split('data-repro-section="',1)[0].split('</section>',1)[0]
        return set(map(int,re.findall(r'class="repro-photo" href="/reproduction-center\?animal=(\d+)"',part)))

    def test_all_32_females_visible_without_counting_birth_subset_twice(self):
        html=self.render()
        self.assertIn('Boş / İşlem Bekleyen 6 hayvan: 6 işlem yapılmamış, 0 yeniden işlem bekleyen',html)
        for group,ids in self.groups.items():
            self.assertEqual(self.ids(html,group),set(ids))
        self.assertEqual(self.ids(html,'birth'),set(self.groups['pregnant'][:2]))
        self.assertNotIn('BK-male',html);self.assertNotIn('BK-sold',html)
        self.assertNotIn('data-repro-filter="unprocessed"',html)
        self.assertIn('gebelik durumu doğrulanmadı',html)

    def test_uncertain_and_birth_closed_animals_remain_visible(self):
        aid=self.groups['control'][0]
        closed=self.groups['pregnant'][0]
        with server.db() as con:
            server.set_latest_pregnancy_result(con,self.ins[aid],'Belirsiz')
            con.execute("update inseminations set pregnancy_result='Doğum',due_date='' where id=?",(self.ins[closed],))
        html=self.render()
        self.assertEqual(self.ids(html,'uncertain'),{aid})
        self.assertEqual(self.ids(html,'control'),{self.groups['control'][1]})
        self.assertEqual(self.ids(html,'empty'),set(self.groups['empty'])|{closed})
        self.assertIn('Boş / İşlem Bekleyen 7 hayvan: 6 işlem yapılmamış, 1 yeniden işlem bekleyen',html)
        self.assertIn('value="Belirsiz"',html)
        self.assertIn('data-current="Belirsiz"',html)


if __name__=='__main__':
    unittest.main()
