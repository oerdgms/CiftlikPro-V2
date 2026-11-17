import unittest
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
