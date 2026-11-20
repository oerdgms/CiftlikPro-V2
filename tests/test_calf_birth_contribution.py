import unittest
from datetime import timedelta
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import test_app_edition as fixture
import mobile_reference

server = fixture.server


class CalfBirthContributionTests(unittest.TestCase):
    setUp = fixture.AppEditionTests.setUp
    tearDown = fixture.AppEditionTests.tearDown
    get = fixture.AppEditionTests.get

    def post(self, path, **fields):
        request = Request(self.base + path, urlencode(fields).encode(),
                          headers={'Cookie': 'sid=app-edition-test'})
        with urlopen(request, timeout=10) as response:
            return response.read().decode()

    def newborn_fields(self, mother, **changes):
        fields=dict(tag='TR583099990',gender='Dişi',breed='Simental',
                    birth_date=server.date.today().isoformat(),arrival_source='Çiftlikte Doğdu',
                    mother_id=mother,birth_internal_value='40000,25')
        fields.update(changes)
        return fields

    def test_newborn_registration_value_and_later_edit_without_cash_or_duplicate(self):
        with server.db() as c:
            mother=c.execute("insert into animals(tag,gender,purchase_price,entry_date) values('NEW-MOTHER','Dişi',150000,?)",(server.date.today().isoformat(),)).lastrowid
            before=c.execute('select count(*) from finance').fetchone()[0]
        page=self.get('/animal-add')[2].decode()
        self.assertIn('name="birth_internal_value"',page)
        self.assertIn('Doğum / İç Üretim Değeri',page)
        quick=self.get(f'/animal-events?source=animal&id={mother}&event=birth')[2].decode()
        self.assertIn('name="birth_internal_value"',quick)
        result=self.post('/animal-add',**self.newborn_fields(mother))
        self.assertIn('başarıyla kaydedildi',result)
        with server.db() as c:
            calf=c.execute("select * from calves where tag='TR583099990'").fetchone()
            self.assertIsNotNone(calf)
            cid=calf['id']
            row=c.execute('select * from calf_internal_costs where calf_id=?',(cid,)).fetchone()
            self.assertEqual((row['amount'],row['cost_date'],row['quantity'],row['cost_type']),(40000.25,calf['birth_date'],1,server.CALF_BIRTH_COST))
            m=c.execute('select * from animals where id=?',(mother,)).fetchone()
            self.assertEqual(server.animal_financial_summary(c,m)['remaining_net_cost'],109999.75)
        self.post('/calf-internal-cost/save',calf_id=cid,cost_type=server.CALF_BIRTH_COST,quantity=1,unit_cost=42000)
        self.post('/animal-add',**self.newborn_fields(mother))
        with server.db() as c:
            self.assertEqual(c.execute('select count(*) from finance').fetchone()[0],before)
            self.assertEqual([r[0] for r in c.execute('select amount from calf_internal_costs where calf_id=?',(cid,))],[42000])

    def test_newborn_blank_value_can_be_added_later(self):
        with server.db() as c:
            mother=c.execute("insert into animals(tag,gender) values('BLANK-MOTHER','Dişi')").lastrowid
        self.post('/animal-add',**self.newborn_fields(mother,birth_internal_value=''))
        with server.db() as c:
            cid=c.execute("select id from calves where tag='TR583099990'").fetchone()[0]
            self.assertEqual(c.execute('select count(*) from calf_internal_costs where calf_id=?',(cid,)).fetchone()[0],0)
        self.post('/calf-internal-cost/save',calf_id=cid,cost_type=server.CALF_BIRTH_COST,quantity=1,unit_cost=40000)
        with server.db() as c:
            self.assertEqual(c.execute('select amount from calf_internal_costs where calf_id=?',(cid,)).fetchone()[0],40000)

    def test_invalid_newborn_value_creates_no_animal_or_financial_record(self):
        with server.db() as c:
            mother=c.execute("insert into animals(tag,gender) values('INVALID-MOTHER','Dişi')").lastrowid
            before=c.execute('select count(*) from finance').fetchone()[0]
        for value in ('-1','NaN','Infinity','abc','1000000000000'):
            self.post('/animal-add',**self.newborn_fields(mother,birth_internal_value=value))
        self.post('/animal-add',**self.newborn_fields(mother,arrival_source='Satın Alındı'))
        with server.db() as c:
            self.assertIsNone(c.execute("select id from calves where tag='TR583099990'").fetchone())
            self.assertIsNone(c.execute("select id from animals where tag='TR583099990'").fetchone())
            self.assertEqual(c.execute('select count(*) from calf_internal_costs').fetchone()[0],0)
            self.assertEqual(c.execute('select count(*) from finance').fetchone()[0],before)

    def test_newborn_failure_rolls_back_calf_and_birth_value_together(self):
        from unittest.mock import patch
        with server.db() as c:
            mother=c.execute("insert into animals(tag,gender) values('ROLLBACK-MOTHER','Dişi')").lastrowid
        with patch.object(server,'close_pregnancy_after_birth',side_effect=RuntimeError('test rollback')):
            self.post('/animal-add',**self.newborn_fields(mother))
        with server.db() as c:
            self.assertIsNone(c.execute("select id from calves where tag='TR583099990'").fetchone())
            self.assertEqual(c.execute('select count(*) from calf_internal_costs').fetchone()[0],0)

    def test_old_calf_without_mother_can_save_then_link_birth_cost(self):
        birth = (server.date.today() - timedelta(days=60)).isoformat()
        with server.db() as c:
            calf = c.execute("insert into calves(tag,gender,mother_id,birth_date) values('OLD-CALF','Dişi',0,?)", (birth,)).lastrowid
            mother = c.execute("insert into animals(tag,gender) values('OLD-MOTHER','Dişi')").lastrowid
            before = c.execute('select count(*) from finance').fetchone()[0]
        page = self.get(f'/calf?id={calf}')[2].decode()
        self.assertIn('value="Doğum Maliyeti"', page)
        self.assertIn('anne bilgisini tamamlayın', page)
        self.assertIn('2 ay (60 gün)', page)
        result = self.post('/calf-internal-cost/save', calf_id=calf,
                           cost_type=server.CALF_BIRTH_COST, quantity=1,
                           unit_cost=40000, cost_date=server.date.today().isoformat())
        self.assertIn('üretim katkısı henüz anneye yansıtılmadı', result)
        with server.db() as c:
            entry = c.execute('select * from calf_internal_costs where calf_id=?', (calf,)).fetchone()
            self.assertEqual((entry['cost_date'], entry['amount']), (birth,40000))
            self.assertEqual(c.execute('select count(*) from finance').fetchone()[0], before)
            m = c.execute('select * from animals where id=?', (mother,)).fetchone()
            self.assertEqual(server.animal_financial_summary(c,m)['birth_contribution'],0)
            c.execute('update calves set mother_id=? where id=?', (mother,calf))
        with server.db() as c:
            m = c.execute('select * from animals where id=?', (mother,)).fetchone()
            self.assertEqual(server.animal_financial_summary(c,m)['birth_contribution'],40000)
        mobile = mobile_reference.detail_markup(vars(server), f'/calf?id={calf}', lambda *args:'')
        self.assertIn(f'class="cp-ref-family-link" href="/animal?id={mother}"', mobile)
        self.assertIn('OLD-MOTHER', mobile)

    def test_60_day_calf_with_mother_can_update_one_birth_cost(self):
        birth = (server.date.today() - timedelta(days=60)).isoformat()
        with server.db() as c:
            mother = c.execute("insert into animals(tag,gender) values('MOTHER-60','Dişi')").lastrowid
            calf = c.execute("insert into calves(tag,gender,mother_id,birth_date) values('CALF-60','Erkek',?,?)", (mother,birth)).lastrowid
        for amount in (40000,42000):
            self.post('/calf-internal-cost/save', calf_id=calf, cost_type=server.CALF_BIRTH_COST,
                      quantity=1,unit_cost=amount)
        with server.db() as c:
            entries=c.execute('select amount,cost_date from calf_internal_costs where calf_id=?',(calf,)).fetchall()
            self.assertEqual([tuple(r) for r in entries],[(42000,birth)])

    def test_age_day_boundaries_and_invalid_dates(self):
        for days, expected in ((44,'44 gün'),(59,'59 gün'),(60,'2 ay (60 gün)'),(731,'2 yıl 0 ay (731 gün)')):
            birth=(server.date.today()-timedelta(days=days)).isoformat()
            self.assertEqual(server.age_text(birth),expected)
        self.assertEqual(server.age_text(''),'-')
        self.assertEqual(server.age_text('invalid'),'-')
        self.assertEqual(server.age_text((server.date.today()+timedelta(days=1)).isoformat()),'-')

    def test_all_birth_years_reduce_remaining_cost_without_cash_income(self):
        today = server.date.today()
        with server.db() as c:
            mother=c.execute("insert into animals(tag,gender,purchase_price,entry_date) values('YEAR-MOTHER','Dişi',150000,?)",(today.isoformat(),)).lastrowid
            calves=[]
            for tag,age in (('YEAR-CALF-1',365),('YEAR-CALF-2',1)):
                calves.append(c.execute("insert into calves(tag,gender,mother_id,birth_date) values(?,'Dişi',?,?)",(tag,mother,(today-timedelta(days=age)).isoformat())).lastrowid)
            c.execute("insert into finance(tx_date,tx_type,category,amount,animal_id,created_at) values(?,'Gelir','Süt Satışı',50000,?,?)",(today.isoformat(),mother,today.isoformat()))
            ledger_count=c.execute('select count(*) from finance').fetchone()[0]
        def save(calf,amount):
            self.post('/calf-internal-cost/save',calf_id=calf,cost_type=server.CALF_BIRTH_COST,quantity=1,unit_cost=amount)
        def summary():
            with server.db() as c:
                rec=c.execute('select * from animals where id=?',(mother,)).fetchone()
                self.assertEqual(c.execute('select count(*) from finance').fetchone()[0],ledger_count)
                return server.animal_financial_summary(c,rec)
        save(calves[0],40000);save(calves[1],45000)
        result=summary()
        self.assertEqual((result['total_cost'],result['income'],result['birth_contribution'],result['remaining_net_cost']),(150000,50000,85000,15000))
        self.assertEqual(result['card_net_profit'],-15000)
        self.assertEqual(len(result['birth_contributions']),2)
        desktop=self.get(f'/animal?id={mother}')[2].decode()
        mobile=mobile_reference.detail_markup(vars(server),f'/animal?id={mother}',lambda *args:'')
        for page in (desktop,mobile):
            self.assertIn('Kalan Net Maliyet',page)
            self.assertIn('₺15.000,00',page)
        save(calves[1],50000)
        self.assertEqual(summary()['remaining_net_cost'],10000)
        with server.db() as c:
            rid=c.execute('select id from calf_internal_costs where calf_id=?',(calves[0],)).fetchone()[0]
        self.post('/calf-internal-cost/delete',calf_id=calves[0],id=rid)
        self.assertEqual(summary()['remaining_net_cost'],50000)
        save(calves[1],120000)
        result=summary()
        self.assertEqual((result['remaining_net_cost'],result['cost_surplus']),(0,20000))

    def test_birth_transfer_changes_card_net_without_posting_to_finance(self):
        today = server.date.today().isoformat()
        with server.db() as c:
            mother = c.execute("insert into animals(tag,gender) values('TEST-ANNE','Dişi')").lastrowid
            calf = c.execute("""insert into calves(tag,gender,mother_id,birth_date)
                values('TEST-BUZAGI','Dişi',?,?)""", (mother,today)).lastrowid
            c.execute("""insert into finance(tx_date,tx_type,category,amount,animal_id,created_at)
                values(?,'Gelir','Süt Satışı',70000,?,?)""", (today,mother,today))

        def summaries():
            with server.db() as c:
                a = c.execute('select * from animals where id=?',(mother,)).fetchone()
                ca = c.execute('select * from calves where id=?',(calf,)).fetchone()
                return (server.animal_financial_summary(c,a),
                        server.animal_financial_summary(c,ca,'calf'),
                        c.execute('select count(*) from finance').fetchone()[0])

        def save(kind, amount):
            return self.post('/calf-internal-cost/save', calf_id=calf, cost_type=kind,
                             quantity=1, unit_cost=amount, cost_date=today)

        save('Bakım', 250)
        self.assertIn('anne kartına üretim katkısı',save(server.CALF_BIRTH_COST,40000))
        a,ca,count = summaries()
        self.assertEqual((a['income'],a['birth_contribution'],a['card_net_profit']), (70000,40000,110000))
        self.assertEqual((ca['total_cost'],count),(40250,1))
        marker = 'Buzağı Üretim Katkısı'
        self.assertIn(marker,self.get(f'/animal?id={mother}')[2].decode())
        mobile = mobile_reference.detail_markup(vars(server),f'/animal?id={mother}',lambda *args: '')
        self.assertIn(marker,mobile)
        self.assertIn(f'/calf?id={calf}',mobile)
        row_id = a['birth_contributions'][0]['calf_id']
        self.assertEqual(row_id,calf)
        save(server.CALF_BIRTH_COST,35000)
        a,ca,count = summaries()
        self.assertEqual((a['birth_contribution'],ca['total_cost'],count),(35000,35250,1))
        self.assertEqual(len(a['birth_contributions']),1)

        with server.db() as c:
            rid = c.execute('select id from calf_internal_costs where calf_id=? and cost_type=?',
                            (calf,server.CALF_BIRTH_COST)).fetchone()[0]
        self.post('/calf-internal-cost/delete',id=rid,calf_id=calf)
        a,ca,count = summaries()
        self.assertEqual((a['birth_contribution'],ca['total_cost'],count),(0,250,1))
