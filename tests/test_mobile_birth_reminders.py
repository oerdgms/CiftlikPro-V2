"""Expected births in mobile jobs and notifications use current pregnancies."""
from datetime import timedelta
from html.parser import HTMLParser
import unittest

import test_app_edition as app_tests

server = app_tests.server


class BirthRows(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.rows = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'div' and attrs.get('data-cp-kind') == 'birth':
            self.rows.append(attrs)
        if tag == 'a' and attrs.get('class') == 'cp-task-action' and attrs.get('href','').endswith('#reproduction'):
            if self.rows:
                self.rows[-1].setdefault('href',attrs['href'])


class MobileBirthReminderTests(unittest.TestCase):
    setUp = app_tests.AppEditionTests.setUp
    tearDown = app_tests.AppEditionTests.tearDown
    get = app_tests.AppEditionTests.get

    def seed_births(self):
        today = server.date.today()
        data = [('GEÇMİŞ', -3, 'Aktif'), ('BUGÜN', 0, 'Aktif'), ('YAKIN', 45, 'Aktif'),
                ('UZAK', 46, 'Aktif'), ('KAPALI', 5, 'Aktif'), ('SATILAN', 3, 'Satıldı'),
                ('HATALI', None, 'Aktif'), ('YENİNEGATİF', 7, 'Aktif')]
        ids = {}
        with server.db() as c:
            for tag, offset, status in data:
                aid = c.execute("insert into animals(tag,gender,status) values(?,'Dişi',?)",(tag,status)).lastrowid
                ids[tag] = aid
                due = today+timedelta(days=offset) if offset is not None else None
                c.execute('insert into inseminations(animal_id,attempt,insemination_date,pregnancy_result,due_date) values(?,1,?,?,?)',
                          (aid,((due or today)-timedelta(days=280)).isoformat(),'Pozitif',due.isoformat() if due else 'geçersiz'))
            c.execute("insert into calves(tag,mother_id,gender,birth_date,status) values('BUZAĞI',?,'Dişi',?,'Aktif')",(ids['KAPALI'],today.isoformat()))
            c.execute("insert into inseminations(animal_id,attempt,insemination_date,pregnancy_result) values(?,2,?,'Negatif')",(ids['YENİNEGATİF'],today.isoformat()))
            c.execute("insert into finance(tx_date,tx_type,category,amount,description,payment_method,due_date,payment_status,created_at) values(?,'Gider','Yem',100,'Vade','Vadeli',?,'Bekliyor',?)",(today.isoformat(),today.isoformat(),today.isoformat()))
        return ids

    def test_due_today_upcoming_overdue_link_and_closed_exclusions(self):
        ids = self.seed_births()
        html = self.get('/?app_view=tasks&filter=birth')[2].decode()
        rows = BirthRows(html).rows
        self.assertEqual([(r['data-cp-state'],r['href'].split('#')[0].split('id=')[1].split('&')[0]) for r in rows],
                         [('overdue',str(ids['GEÇMİŞ'])),('today',str(ids['BUGÜN'])),('upcoming',str(ids['YAKIN']))])
        self.assertTrue(all(r['href'].endswith('#reproduction') for r in rows))
        self.assertIn('data-cp-task-filter="birth">Doğumlar<span>3</span>',html)
        self.assertIn('Tarih 3 gün önce geçti',html)
        self.assertIn('Tahmini tarih:',html)
        self.assertIn('data-cp-kind="finance"',html)
        _,_,detail,_ = self.get(rows[1]['href'].split('#')[0])
        self.assertIn('data-ref-section="reproduction"',detail.decode())
        with server.db() as c:
            c.execute("update inseminations set pregnancy_result='Doğum' where animal_id=?",(ids['BUGÜN'],))
        html = self.get('/?app_view=tasks')[2].decode()
        self.assertEqual([r['data-cp-state'] for r in BirthRows(html).rows],['overdue','upcoming'])

    def test_tasks_show_today_completions_and_link_to_animal(self):
        today = server.date.today()
        with server.db() as c:
            animal = c.execute("insert into animals(tag,gender,status) values('TEST-KÜPE','Dişi','Aktif')").lastrowid
            c.execute("insert into health(animal_id,kind,product,applied_date) values(?,'Aşı','BUGÜN-AŞI',?)",(animal,today.isoformat()))
            c.execute("insert into health(animal_id,kind,product,applied_date) values(?,'Aşı','DÜN-AŞI',?)",(animal,(today-timedelta(days=1)).isoformat()))
            c.execute("insert into health(animal_id,kind,product,next_date) values(?,'Aşı','BEKLEYEN-AŞI',?)",(animal,today.isoformat()))
        jobs = self.get('/?app_view=tasks&filter=done')[2].decode()
        self.assertIn('data-cp-task-filter="done">Bugün Yapılanlar<span>1</span>',jobs)
        self.assertIn('>BUGÜN-AŞI</a>',jobs)
        self.assertNotIn('>DÜN-AŞI</a>',jobs)
        self.assertIn(f'class="cp-task-animal" href="/animal?id={animal}">TEST-KÜPE</a>',jobs)
        home = self.get('/')[2].decode()
        self.assertNotIn('>BUGÜN-AŞI</a>',home)
        self.assertNotIn('cp-ref-home-foot',home)
        health = self.get('/health?from_tasks=1')[2].decode()
        self.assertIn('Görevlere dön</a>',health)
        self.assertIn(f'class="cp-task-animal" href="/animal?id={animal}">TEST-KÜPE</a>',health)

    def test_bell_lists_birth_once_and_keeps_its_60_day_window(self):
        ids = self.seed_births()
        html = self.get('/notifications')[2].decode()
        self.assertEqual(html.count('BUGÜN · Beklenen Doğum'),1)
        self.assertIn('UZAK · Beklenen Doğum',html)
        self.assertNotIn('KAPALI · Beklenen Doğum',html)
