import sqlite3
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
import test_multi_farm as mf
import multi_farm

class LoginResilienceTests(unittest.TestCase):
 setUp=mf.MultiFarmTests.setUp
 request=mf.MultiFarmTests.request
 create=mf.MultiFarmTests.create
 def test_allowed_login_verifies_password_once(self):
  farm=self.create()
  with patch.object(mf.server,'password_verify',wraps=mf.server.password_verify) as verify:
   status,_,_=self.request('/login',{'username':'admin','password':'test-admin-123','login_farm':farm['id']},sid='')
  self.assertEqual(status,303);self.assertEqual(verify.call_count,1)
 def test_unchanged_accounts_skip_target_and_changed_password_syncs(self):
  farm=self.create()
  with patch.object(multi_farm.Registry,'_write_accounts',autospec=True,side_effect=multi_farm.Registry._write_accounts) as write:
   for _ in range(3):self.registry.sync_accounts(farm)
   self.assertEqual(write.call_count,0)
   with mf.server.db() as c:c.execute("update users set full_name='Changed' where username='admin'")
   with ThreadPoolExecutor(max_workers=5) as pool:list(pool.map(lambda _:self.registry.sync_accounts(farm),range(10)))
   self.assertEqual(write.call_count,1)
   self.registry.sync_accounts(farm,force=True);self.assertEqual(write.call_count,2)
  with multi_farm.scope(farm):
   with mf.server.db() as c:self.assertEqual(c.execute("select full_name from users where username='admin'").fetchone()[0],'Changed')
 def test_locked_get_has_readable_no_store_retry_and_recovers(self):
  farm=self.create()
  with patch.object(multi_farm.Registry,'sync_accounts',side_effect=sqlite3.OperationalError('database is locked')):
   status,headers,body=self.request('/?farm='+farm['id'])
  self.assertEqual(status,503);self.assertIn('Yeniden dene',body.decode());self.assertEqual(headers['Cache-Control'],'no-store')
  self.assertEqual(self.request('/?farm='+farm['id'])[0],200)
 def test_photo_get_does_not_sync_users(self):
  farm=self.create()
  with patch.object(multi_farm.Registry,'sync_accounts',side_effect=AssertionError('Photo must not sync')):
   self.assertEqual(self.request('/photo-preview?name=missing.jpg&farm='+farm['id'])[0],404)
 def test_settings_alias_and_one_business_menu_destination(self):
  farm=self.create()
  status,headers,_=self.request('/settings?farm='+farm['id']);self.assertEqual(status,303);self.assertIn('/farm-profile?',headers['Location']);self.assertIn(farm['id'],headers['Location'])
  text=self.request('/all-animals?farm='+farm['id'])[2].decode()
  self.assertEqual(text.count('class="cp-ref-business-link"'),1)
  self.assertIn('İşletmeler · Değiştir',text)
 def test_login_database_error_returns_form_without_replaying_password(self):
  farm=self.create()
  with patch.object(mf.server,'password_verify',side_effect=sqlite3.OperationalError('database is locked')):
   status,headers,_=self.request('/login',{'username':'admin','password':'secret-not-in-url','login_farm':farm['id']},sid='')
  self.assertEqual(status,303);self.assertIn('/login?',headers['Location']);self.assertIn(farm['id'],headers['Location']);self.assertNotIn('secret-not-in-url',headers['Location']);self.assertIsNone(headers.get('Set-Cookie'))

if __name__=='__main__':unittest.main()
