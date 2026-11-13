import unittest
from datetime import timedelta

import test_app_edition as app_tests
import mobile_reference as ref
import release_info as release

server = app_tests.server


class FinancePWAAccessTests(unittest.TestCase):
    setUp = app_tests.AppEditionTests.setUp
    tearDown = app_tests.AppEditionTests.tearDown
    get = app_tests.AppEditionTests.get
    seed = app_tests.AppEditionTests.seed

    def test_signed_in_pages_have_update_entry_and_public_fallback_remains(self):
        login = self.get('/login',False)[2].decode()
        self.assertNotIn('href="/app-install"',login)
        for route in ('/modules','/'):
            html = self.get(route)[2].decode()
            self.assertEqual(html.count('href="/app-install"'),1,route)
            self.assertNotIn('id="cpInstall"',html,route)
        status, _, body, _ = self.get('/app-install',False)
        self.assertEqual(status,200)
        html = body.decode()
        self.assertIn('Güncellemeyi kontrol et → Yeni sürümü aç',html)
        self.assertIn(release.BUILD,html)
        self.assertIn('/app-assets/pwa.js?v='+release.VERSION,html)

    def test_desktop_female_male_and_calf_finance_share_residence(self):
        _, _, female, male, calf = self.seed()
        entry = (server.date.today()-timedelta(days=78)).isoformat()
        for source,table,sid in [('animal','animals',female),('animal','animals',male),('calf','calves',calf)]:
            with server.db() as c:
                c.execute(f'update {table} set entry_date=? where id=?',(entry,sid))
            html = self.get(f'/{source}?id={sid}')[2].decode()
            self.assertEqual(html.count('cp-wide-only cp-wide-residence'),1)
            desktop = html.split('cp-wide-only cp-wide-residence',1)[1].split('</dl>',1)[0]
            self.assertIn('78 gün',desktop)
            self.assertIn(server.fmt_date(entry),desktop)

    def test_all_finance_rows_have_readable_details_and_preserve_allocated_amounts(self):
        _, _, female, male, _ = self.seed()
        description = '<script>unsafe</script> '+'TR583074657, '*40
        with server.db() as c:
            for i in range(7):
                c.execute("insert into finance(tx_date,tx_type,category,description,amount,animal_id,created_at) values(?,?,?,?,?,?,?)",
                          (server.date.today().isoformat(),'Gider','Aşı',description,100+i,female,server.datetime.now().isoformat()))
            fid=c.execute("insert into finance(tx_date,tx_type,category,description,amount,created_at) values(?,?,?,?,?,?)",
                          (server.date.today().isoformat(),'Gelir','Süt Satışı','Toplu süt',1000,server.datetime.now().isoformat())).lastrowid
            for aid in (female,male):c.execute('insert into finance_animals(finance_id,animal_id) values(?,?)',(fid,aid))
            record=c.execute('select * from animals where id=?',(female,)).fetchone()
            financial=server.animal_financial_summary(c,record)
        text=ref.finance_records_markup(vars(server),financial)
        self.assertEqual(text.count('data-finance-record='),8)
        self.assertNotIn('<table',text)
        self.assertNotIn('<script>',text)
        self.assertIn('&lt;script&gt;',text)
        self.assertIn(server.money(500),text)
        self.assertIn('2 hayvandan payı',text)
        self.assertIn('/finance/edit?id='+str(fid),text)
