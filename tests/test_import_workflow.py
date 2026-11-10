import io,json,re,unittest,urllib.request,urllib.error
from urllib.parse import parse_qs,urlsplit
from PIL import Image
import test_multi_farm as mf
import release_info

class ImportWorkflowTests(unittest.TestCase):
 setUp=mf.MultiFarmTests.setUp
 create=mf.MultiFarmTests.create
 request=mf.MultiFarmTests.request
 def upload(self,filename,content,farm='primary',ajax=True):
  boundary='cp-import-test';body=(f'--{boundary}\r\nContent-Disposition: form-data; name="animal_file"; filename="{filename}"\r\nContent-Type: application/octet-stream\r\n\r\n').encode()+content+f'\r\n--{boundary}--\r\n'.encode()
  headers={'Cookie':'sid=farm-admin','Content-Type':'multipart/form-data; boundary='+boundary}
  if ajax:headers['Accept']='application/json'
  request=urllib.request.Request(self.base+'/animals/import-preview?farm='+farm,data=body,headers=headers)
  try:
   with urllib.request.build_opener(mf.NoRedirect).open(request,timeout=30) as r:return r.status,r.headers,r.read()
  except urllib.error.HTTPError as r:return r.code,r.headers,r.read()
 def test_links_and_old_report_tab_open_dedicated_page(self):
  farm=self.create();fid=farm['id']
  for route in ['/data?farm='+fid,'/reports?tab=animals&farm='+fid]:
   status,_,body=self.request(route);self.assertEqual(status,200);text=body.decode()
   self.assertIn('/animals/import?farm='+fid,text);self.assertNotIn('/reports#animal-import',text)
  status,headers,_=self.request('/reports?tab=import&farm='+fid)
  self.assertEqual(status,303);self.assertEqual(urlsplit(headers['Location']).path,'/animals/import');self.assertEqual(parse_qs(urlsplit(headers['Location']).query)['farm'],[fid])
  status,_,body=self.request('/animals/import?farm='+fid);self.assertEqual(status,200);self.assertIn('data-animal-import-form',body.decode());self.assertIn('import.js?v='+release_info.VERSION,body.decode())
 def test_csv_preview_confirmation_is_separate_and_scoped(self):
  farm=self.create();fid=farm['id'];csv='Küpe No;Cinsiyet;Doğum Tarihi;Irk\nTR123456789012;Erkek;01/07/2025;Simental\n'.encode('utf-8-sig')
  status,_,body=self.upload('animals.csv',csv,fid);self.assertEqual(status,200,body[:200]);data=json.loads(body);self.assertTrue(data['ok'])
  with mf.farms.scope(farm):
   with mf.server.db() as c:self.assertEqual(c.execute('select count(*) from animals').fetchone()[0],0)
  status,_,body=self.request(data['redirect']);self.assertEqual(status,200);self.assertIn('TR123456789012',body.decode());self.assertIn('cp-import-row',body.decode())
  token=parse_qs(urlsplit(data['redirect']).query)['token'][0]
  self.assertEqual(self.request('/animals/import-confirm?farm='+fid,{'token':token})[0],303)
  with mf.farms.scope(farm):
   with mf.server.db() as c:self.assertEqual(c.execute('select count(*) from animals').fetchone()[0],1)
  with mf.server.db() as c:self.assertIsNone(c.execute("select id from animals where tag='TR123456789012'").fetchone())
  self.request('/animals/import-confirm?farm='+fid,{'token':token})
  with mf.farms.scope(farm):
   with mf.server.db() as c:self.assertEqual(c.execute('select count(*) from animals').fetchone()[0],1)
 def test_scanned_pdf_returns_json_error_and_native_retry_page(self):
  output=io.BytesIO();Image.new('RGB',(200,300),'white').save(output,format='PDF')
  for ajax in (True,False):
   status,headers,body=self.upload('scan.pdf',output.getvalue(),ajax=ajax)
   self.assertEqual(status,422)
   if ajax:self.assertIn('OCR',json.loads(body)['message'])
   else:self.assertIn('data-animal-import-form',body.decode());self.assertIn('seçilebilir metin',body.decode())
  with mf.server.db() as c:self.assertEqual(c.execute('select count(*) from animals').fetchone()[0],1)
 def test_invalid_file_and_empty_input_do_not_create_preview(self):
  self.assertEqual(self.upload('bad.txt',b'bad')[0],422)
  status,_,body=self.upload('blank.csv',b'Kuppe;Gender\n');self.assertEqual(status,422);self.assertFalse(json.loads(body)['ok'])
 def test_other_business_and_staff_cannot_open_preview(self):
  a=self.create('A');b=self.create('B')
  status,_,body=self.upload('x.csv','Küpe No;Cinsiyet;Doğum Tarihi;Irk\nTR123456789013;Erkek;01/07/2025;Simental\n'.encode(),a['id']);self.assertEqual(status,200)
  path=json.loads(body)['redirect'];token=parse_qs(urlsplit(path).query)['token'][0]
  self.assertEqual(self.request('/animals/import-preview?token='+token+'&farm='+b['id'])[0],422)
  self.assertEqual(self.request('/animals/import?farm=primary',sid='farm-staff')[0],303)
 def test_text_pdf_is_read_and_only_previewed(self):
  import reportlab
  from reportlab.pdfgen import canvas
  from reportlab.pdfbase import pdfmetrics
  from reportlab.pdfbase.ttfonts import TTFont
  from pathlib import Path
  pdfmetrics.registerFont(TTFont('ImportTest',str(Path(reportlab.__file__).parent/'fonts/Vera.ttf')))
  output=io.BytesIO();page=canvas.Canvas(output);page.setFont('ImportTest',10)
  page.drawString(30,800,'TR123456789016 1 SIĞIR Simental ERKEK 01/07/2025 02/02/2026');page.save()
  status,_,body=self.upload('official.pdf',output.getvalue());self.assertEqual(status,200,body[:200]);self.assertTrue(json.loads(body)['ok'])
  with mf.server.db() as c:self.assertIsNone(c.execute("select id from animals where tag='TR123456789016'").fetchone())
