import re
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs,urlsplit
import test_multi_farm as mf
import login_experience
import release_info

class LoginExperienceTests(unittest.TestCase):
 def setUp(self):
  mf.MultiFarmTests.setUp(self)
  existing=set(mf.server.SESSIONS)
  self.addCleanup(lambda:[mf.server.SESSIONS.pop(sid,None) for sid in set(mf.server.SESSIONS)-existing])
 request=mf.MultiFarmTests.request
 create=mf.MultiFarmTests.create
 def login(self,farm='primary',username='admin',password='test-admin-123'):
  return self.request('/login',{'username':username,'password':password,'login_farm':farm},sid='')
 def test_public_login_has_names_only_preload_and_inline_photo(self):
  a=self.create('İşletme A <test>');self.create('İşletme B')
  status,_,body=self.request('/login?login_farm='+a['id'],sid='');text=body.decode()
  self.assertEqual(status,200);self.assertIn('name="login_farm"',text);self.assertIn('İşletme A &lt;test&gt;',text)
  self.assertIn('value="'+a['id']+'" selected',text)
  self.assertNotIn('FIRST-ANIMAL',text);self.assertNotIn('test-admin-123',text)
  self.assertIn('rel="preload" as="image" href="/app-assets/login.jpg?v='+release_info.VERSION+'"',text)
  self.assertIn('data:image/jpeg;base64,',text)
  self.assertLess(text.index('rel="preload"'),text.index('<style>'))
  self.assertIn('name="password"',text);self.assertIn('/forgot-password',text);self.assertNotIn('data-cp-pwa-open',text)
 def test_login_selected_farm_sets_session_and_remember_cookie(self):
  a=self.create();status,headers,_=self.login(a['id'])
  self.assertEqual(status,303);self.assertEqual(parse_qs(urlsplit(headers['Location']).query)['farm'],[a['id']])
  cookies=headers.get_all('Set-Cookie');self.assertEqual(len(cookies),2)
  sid=next(x for x in cookies if x.startswith('sid=')).split(';')[0].split('=',1)[1]
  mf.server_session=mf.server.SESSIONS[sid];self.assertEqual(mf.server_session['active_farm'],a['id'])
  self.addCleanup(lambda:mf.server.SESSIONS.pop(sid,None))
  remembered=next(x for x in cookies if x.startswith('cp_login_farm='))
  text=self.request('/login',sid='',headers={'Cookie':remembered.split(';')[0]})[2].decode()
  self.assertIn('value="'+a['id']+'" selected',text)
 def test_staff_without_permission_gets_no_session(self):
  a=self.create();before=set(mf.server.SESSIONS)
  status,headers,_=self.login(a['id'],'staff','test-staff-123')
  self.assertEqual(status,303);self.assertTrue(headers['Location'].startswith('/login?'))
  self.assertIsNone(headers.get('Set-Cookie'));self.assertEqual(set(mf.server.SESSIONS),before)
  with self.registry.connect() as c:c.execute('insert into enterprise_access values(?,?)',(a['id'],'staff'))
  status,headers,_=self.login(a['id'],'staff','test-staff-123');self.assertEqual(status,303);self.assertTrue(headers.get('Set-Cookie'))
 def test_wrong_password_keeps_selection_without_setting_cookie(self):
  a=self.create();status,headers,_=self.login(a['id'],password='wrong-password')
  self.assertEqual(status,303);self.assertIsNone(headers.get('Set-Cookie'))
  self.assertEqual(parse_qs(urlsplit(headers['Location']).query)['login_farm'],[a['id']])
 def test_invalid_business_and_inactive_account_cannot_create_session(self):
  a=self.create();before=set(mf.server.SESSIONS)
  self.assertEqual(self.login('f_0000000000000000')[1].get('Set-Cookie'),None)
  with mf.server.db() as c:c.execute("update users set active=0 where username='staff'")
  self.assertIsNone(self.login(a['id'],'staff','test-staff-123')[1].get('Set-Cookie'))
  self.assertEqual(before,set(mf.server.SESSIONS))
 def test_legacy_login_without_field_uses_primary_and_license_still_required(self):
  status,headers,_=self.request('/login',{'username':'admin','password':'test-admin-123'},sid='')
  self.assertEqual(status,303);self.assertEqual(parse_qs(urlsplit(headers['Location']).query)['farm'],['primary'])
  with patch.object(mf.server,'license_status',return_value=(False,{},'Lisans gerekli')):
   status,headers,_=self.login();self.assertEqual(status,303);self.assertTrue(headers['Location'].startswith('/license'));self.assertIsNone(headers.get('Set-Cookie'))
