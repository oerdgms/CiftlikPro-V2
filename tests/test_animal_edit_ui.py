"""Fixed TR prefixes must round-trip through the existing edit handlers safely."""
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlencode

from test_reports_import import server


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args):return None


class AnimalEditTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.paths=patch.multiple(server,DB=Path(self.temp.name)/'edit.db',UPLOADS=Path(self.temp.name)/'uploads')
        self.paths.start();server.init_db()
        self.license=patch.object(server,'license_status',return_value=(True,{},''));self.license.start()
        with server.db() as c:
            self.adult=c.execute("insert into animals(tag,nickname,gender,status) values('TR583231764','İnci','Dişi','Aktif')").lastrowid
            self.linked=c.execute("insert into calves(tag,mother_id,birth_date,gender,status,promoted_animal_id) values('TR583231764',0,'2025-01-01','Dişi','Aktif',?)",(self.adult,)).lastrowid
            self.calf=c.execute("insert into calves(tag,mother_id,birth_date,gender,status) values('TR583231765',0,'2026-02-10','Dişi','Aktif')").lastrowid
            self.other=c.execute("insert into animals(tag,gender,status) values('TR583231766','Erkek','Aktif')").lastrowid
            self.legacy=c.execute("insert into animals(tag,gender,status) values('OZEL-001','Erkek','Aktif')").lastrowid
        server.SESSIONS['animal-edit-test']={'id':1,'username':'admin','role':'admin'}
        self.http=server.QuietThreadingHTTPServer(('127.0.0.1',0),server.App)
        self.thread=threading.Thread(target=self.http.serve_forever,daemon=True);self.thread.start()
        self.base='http://127.0.0.1:'+str(self.http.server_port)
        self.opener=urllib.request.build_opener(NoRedirect)

    def tearDown(self):
        self.http.shutdown();self.http.server_close();self.thread.join()
        server.SESSIONS.pop('animal-edit-test',None)
        self.license.stop();self.paths.stop();self.temp.cleanup()

    def request(self,path,data=None):
        req=urllib.request.Request(self.base+path,data=urlencode(data).encode() if data is not None else None,headers={'Cookie':'sid=animal-edit-test'})
        try:return self.opener.open(req,timeout=20)
        except urllib.error.HTTPError as response:return response

    def tag(self,table,record_id):
        with server.db() as c:return c.execute('select tag from '+table+' where id=?',(record_id,)).fetchone()[0]

    def form(self,source,record_id,**changes):
        result={'id':record_id,'nickname':'İnci','gender':'Dişi','status':'Aktif','birth_date':'2025-01-01',
                'mother_id':'','purchase_price':'1250.50','daily_care_cost':'2.75','notes':'Not korundu'}
        if 'tag_digits' in changes:result['tag_prefix']='TR'
        result.update(changes);return result

    def test_edit_pages_expose_fixed_prefix_and_keep_full_multipart_form(self):
        for source,sid in [('animal',self.adult),('calf',self.calf)]:
            with self.subTest(source=source),self.request('/'+source+'-edit?id='+str(sid)) as response:
                html=response.read().decode()
                self.assertEqual(response.status,200)
                self.assertIn('data-cp-edit-content',html)
                self.assertIn('name="tag_digits"',html)
                self.assertIn('class="cp-edit-tag-prefix" aria-hidden="true">TR</span>',html)
                self.assertIn('enctype="multipart/form-data"',html)
                self.assertIn('name="photo_file"',html)
                self.assertIn('name="notes"',html)

    def test_adult_digit_edit_updates_linked_calf_once_and_preserves_decimal_fields(self):
        with self.request('/animal-edit',self.form('animal',self.adult,tag_digits='583231770')) as response:
            self.assertEqual(response.status,303)
        self.assertEqual(self.tag('animals',self.adult),'TR583231770')
        self.assertEqual(self.tag('calves',self.linked),'TR583231770')
        with server.db() as c:
            r=c.execute('select purchase_price,daily_care_cost,notes from animals where id=?',(self.adult,)).fetchone()
        self.assertEqual(tuple(r),(1250.50,2.75,'Not korundu'))

    def test_promoted_calf_digit_edit_updates_the_linked_adult(self):
        with self.request('/calf-edit',self.form('calf',self.linked,tag_digits='TR583231771')) as response:
            self.assertEqual(response.status,303)
        self.assertEqual(self.tag('calves',self.linked),'TR583231771')
        self.assertEqual(self.tag('animals',self.adult),'TR583231771')

    def test_duplicate_digits_cannot_overwrite_other_animals_or_calves(self):
        for source,sid,table in [('animal',self.adult,'animals'),('calf',self.calf,'calves')]:
            before=self.tag(table,sid)
            with self.subTest(source=source),self.request('/'+source+'-edit',self.form(source,sid,tag_digits='583231766')) as response:
                self.assertIn('/'+source+'-edit?',response.headers['Location'])
            self.assertEqual(self.tag(table,sid),before)
        self.assertEqual(self.tag('animals',self.other),'TR583231766')

    def test_invalid_digits_never_save_an_empty_or_partial_tag(self):
        for source,sid,table in [('animal',self.adult,'animals'),('calf',self.calf,'calves')]:
            before=self.tag(table,sid)
            for digits in ('','1234567','123456789012345'):
                with self.subTest(source=source,digits=digits),self.request('/'+source+'-edit',self.form(source,sid,tag_digits=digits)) as response:
                    self.assertIn('/'+source+'-edit?',response.headers['Location'])
                self.assertEqual(self.tag(table,sid),before)

    def test_existing_custom_identifiers_keep_their_original_edit_contract(self):
        with self.request('/animal-edit?id='+str(self.legacy)) as response:
            html=response.read().decode()
            self.assertIn('name="tag" required value="OZEL-001"',html)
            self.assertNotIn('name="tag_digits"',html)
        with self.request('/animal-edit',self.form('animal',self.legacy,tag='OZEL-002',gender='Erkek')) as response:
            self.assertEqual(response.status,303)
        self.assertEqual(self.tag('animals',self.legacy),'OZEL-002')


if __name__=='__main__':unittest.main()
