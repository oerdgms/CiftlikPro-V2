import unittest
from datetime import date, timedelta

import mobile_reference as ref
import test_mobile_reference as reference_tests
from test_reports_import import server


class ResidenceDatesTests(unittest.TestCase):
    def test_recorded_entry_wins_over_purchase_and_age(self):
        text = ref.residence_markup({'entry_date':'2026-10-01','purchase_date':'2026-09-01',
                                    'birth_date':'2020-01-01'}, date(2026,10,31))
        self.assertIn('01/10/2026',text)
        self.assertIn('30 gün',text)
        self.assertNotIn('60 gün',text)

    def test_purchase_fallback_and_same_day_zero(self):
        text = ref.residence_markup({'purchase_date':'2026-10-31'}, date(2026,10,31))
        self.assertIn('31/10/2026',text)
        self.assertIn('0 gün',text)

    def test_missing_and_invalid_dates_do_not_infer_from_birth_or_paddock(self):
        for raw in ('', 'not-a-date', '2026-02-30'):
            text = ref.residence_markup({'entry_date':raw,'birth_date':'2020-01-01',
                                        'paddock_id':1}, date(2026,10,31))
            self.assertIn('Giriş tarihi girilmemiş',text)
            self.assertNotIn(' gün',text)

    def test_archived_duration_stops_at_exit(self):
        text = ref.residence_markup({'entry_date':'2026-10-01','status':'Satıldı',
                                    'exit_date':'2026-10-20'}, date(2026,10,31))
        self.assertIn('19 gün',text)
        self.assertNotIn('30 gün',text)

    def test_inconsistent_future_and_unknown_exit_never_invent_duration(self):
        for record, message in [
            ({'entry_date':'2026-11-01'}, 'Giriş tarihi ileride'),
            ({'entry_date':'2026-10-01','status':'Satıldı'}, 'Çıkış tarihi girilmemiş'),
            ({'entry_date':'2026-10-01','status':'Satıldı','exit_date':'2026-09-01'}, 'tarihlerini kontrol edin'),
        ]:
            text = ref.residence_markup(record,date(2026,10,31))
            self.assertIn(message,text)
            self.assertNotIn(' gün',text)


class ResidenceFinanceIntegrationTests(unittest.TestCase):
    setUp = reference_tests.ReferenceMobileTests.setUp
    tearDown = reference_tests.ReferenceMobileTests.tearDown

    def test_animal_and_calf_finance_show_recorded_stay_before_unchanged_costs(self):
        for source, table, sid in [('animal','animals',self.milking),('calf','calves',self.calf)]:
            entry = (self.today-timedelta(days=125)).isoformat()
            with server.db() as c:
                c.execute(f'update {table} set entry_date=? where id=?',(entry,sid))
                record = c.execute(f'select * from {table} where id=?',(sid,)).fetchone()
                before = server.animal_financial_summary(c,record,source)
            text = ref.detail_markup(vars(server),f'/{source}?id={sid}',self.icon)
            section = text.split('data-ref-section="finance"',1)[1].split('</details>',1)[0]
            self.assertIn('125 gün',section)
            self.assertIn(server.fmt_date(entry),section)
            self.assertLess(section.index('cp-ref-residence'),section.index('cp-ref-money-grid'))
            for field in ('income','expense','daily','total_cost','net_profit'):
                self.assertIn(server.money(before[field]),section)
            with server.db() as c:
                after = server.animal_financial_summary(c,record,source)
            self.assertEqual(before,after)
