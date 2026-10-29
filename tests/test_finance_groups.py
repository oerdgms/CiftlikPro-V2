"""A bulk health expense is one visible operation with an unchanged ledger."""
import json
import secrets
import tempfile
import threading
import unittest
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlencode

from test_reports_import import server
import finance_groups as fg
import health_center as hc
import reproduction_sync as sync


class FinanceGroupsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.dbpatch = patch.object(server, 'DB', Path(self.temp.name) / 'finance.db')
        self.clock = patch.object(sync, 'now', return_value=datetime(2026, 10, 24, 15))
        self.dbpatch.start()
        self.clock.start()
        server.init_db()
        self.refs = []
        self.url = '/finance?start=2026-10-01&end=2026-11-30'
        with server.db() as c:
            for n in range(66):
                aid = c.execute("insert into animals(tag,nickname,gender,status) values(?,?,'Dişi','Aktif')", (f'TR583000{n:03d}', 'İnci Sarı' if n == 0 else f'Hayvan {n}')).lastrowid
                self.refs.append('animal:' + str(aid))
            calf = c.execute("insert into calves(tag,mother_id,birth_date,gender,status) values('TR583009999',?,'2026-10-01','Dişi','Aktif')", (int(self.refs[0].split(':')[1]),)).lastrowid
            self.refs.append('calf:' + str(calf))
        self.pid = self.save(self.refs)
        self.complete(self.pid)

    def tearDown(self):
        self.clock.stop()
        self.dbpatch.stop()
        self.temp.cleanup()

    def save(self, refs, category='vaccine', product='Şap Aşısı', cost='100'):
        form = {'category': category, 'product': product, 'start_date': '2026-10-24',
                'subjects_json': json.dumps(refs), 'request_key': secrets.token_urlsafe(24),
                'repeat_value': '6', 'repeat_unit': 'months', 'rapel': 'yes',
                'rapel_days': '21', 'cost': cost}
        with server.db() as c:
            return hc.save_program(vars(server), c, form, 'admin')

    def complete(self, pid, dose=1, limit=None):
        with server.db() as c:
            tasks = [dict(r) for r in c.execute('select * from health_tasks where course_id=? and dose_no=? and cycle_no in (0,1) order by id', (pid, dose))]
        if limit:
            tasks = tasks[:limit]
        data = {'action': 'complete_batch', 'batch_ref': hc.batch_ref(tasks[0]),
                'task_ids': json.dumps([t['id'] for t in tasks]), 'actual_date': '2026-10-24'}
        with server.db() as c:
            return hc.action(vars(server), c, data, 'admin')

    def model(self, extra=''):
        return fg.load(vars(server), self.url + extra)

    def snapshot(self):
        with server.db() as c:
            return {table: [tuple(r) for r in c.execute('select * from ' + table + ' order by id')]
                    for table in ('health', 'finance', 'health_tasks')}

    def test_67_existing_ledger_rows_become_one_operation_without_mutation(self):
        before = self.snapshot()
        model = self.model()
        self.assertEqual(len(model['selected']), 1)
        self.assertEqual(len(model['visible'][0]['members']), 67)
        self.assertEqual(fg.cents(model['visible'][0]['amount']), 670000)
        self.assertEqual(model['raw_count'], 67)
        self.assertEqual(model['pages'], 1)
        self.assertEqual(model['counts']['expense'], 1)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(len(before['finance']), 67)
        self.assertEqual(sum(fg.cents(row[4]) for row in before['finance']), 670000)

    def test_same_name_date_unrelated_records_and_different_programs_stay_separate(self):
        pid = self.save(self.refs[:2])
        self.complete(pid)
        with server.db() as c:
            for _ in range(2):
                c.execute("insert into finance(tx_date,tx_type,category,amount,description,created_at) values('2026-10-24','Gider','Aşı',100,'Şap Aşısı','2026-10-24')")
        model = self.model()
        self.assertEqual(len(model['selected']), 4)
        self.assertEqual(sorted(len(r['members']) for r in model['selected']), [1, 1, 2, 67])

    def test_doses_remain_separate_even_on_same_actual_date_and_description(self):
        self.complete(self.pid, dose=2, limit=2)
        with server.db() as c:
            c.execute("update finance set description='Şap Aşısı'")
        model = self.model()
        self.assertEqual(sorted(len(r['members']) for r in model['selected']), [2, 67])
        self.assertEqual({fg.phase(r) for r in model['selected']}, {'1. doz', '2. doz'})

    def test_grouping_precedes_pagination_and_clamps_stale_page(self):
        with server.db() as c:
            for i in range(28):
                c.execute("insert into finance(tx_date,tx_type,category,amount,description,created_at) values('2026-10-24','Gider','Diğer',1,?,'2026-10-24')", (f'Normal {i}',))
        model = self.model('&per_page=10&page=99')
        self.assertEqual(len(model['selected']), 29)
        self.assertEqual(model['raw_count'], 95)
        self.assertEqual(model['pages'], 3)
        self.assertEqual(model['filters']['page'], 3)
        self.assertEqual(len(model['visible']), 9)
        self.assertEqual(len(model['visible'][-1]['members']), 67)

    def test_search_and_type_category_date_filters_keep_exact_matching_totals(self):
        self.assertEqual(len(self.model('&q='+urlencode({'q':'şap aşısı'})[2:])['selected']), 1)
        match = self.model('&q=TR583000065')
        self.assertEqual(match['raw_count'], 1)
        self.assertEqual(fg.cents(match['selected'][0]['amount']), 10000)
        self.assertEqual(self.model('&type=Gelir')['selected'], [])
        self.assertEqual(self.model('&category=Yem')['selected'], [])
        empty = fg.load(vars(server), '/finance?start=2026-11-01&end=2026-11-30')
        self.assertEqual(empty['selected'], [])

    def test_changed_payment_terms_and_status_filters_do_not_mix_groups(self):
        with server.db() as c:
            fid = c.execute('select min(id) from finance').fetchone()[0]
            c.execute("update finance set payment_method='Vadeli',payment_status='Bekliyor',due_date='2026-01-01' where id=?", (fid,))
        all_rows = self.model()
        self.assertEqual(sorted(len(r['members']) for r in all_rows['selected']), [1, 66])
        pending = self.model('&status=pending')
        self.assertEqual(len(pending['selected']), 1)
        self.assertEqual(pending['counts']['pending'], 1)
        self.assertEqual(pending['counts']['overdue'], 1)
        self.assertEqual(pending['raw_count'], 1)

    def test_per_animal_edit_recalculates_group_total_with_exact_cents(self):
        with server.db() as c:
            record = c.execute('select * from health order by id limit 1').fetchone()
            hid = record['id']
        with server.db() as c:
            hc.edit_record(vars(server), c, {'id': hid, 'applied_date': '2026-10-24',
                           'product': record['product'], 'cost': '100.01', 'notes': ''}, 'admin')
        group = self.model()['selected'][0]
        self.assertEqual(len(group['members']), 67)
        self.assertEqual(fg.cents(group['amount']), 670001)
        self.assertEqual(sum(fg.cents(r['amount']) for r in group['members']), 670001)

    def test_undo_and_repeated_completion_keep_ledger_and_totals_consistent(self):
        self.assertIn('zaten yapılmış', self.complete(self.pid))
        with server.db() as c:
            hid = c.execute('select min(id) from health').fetchone()[0]
        with server.db() as c:
            hc.action(vars(server), c, {'action': 'delete_record', 'health_id': hid}, 'admin')
        group = self.model()['selected'][0]
        self.assertEqual(len(group['members']), 66)
        self.assertEqual(fg.cents(group['amount']), 660000)
        with server.db() as c:
            self.assertEqual(c.execute('select count(*) from finance').fetchone()[0], 66)

    def test_legacy_course_is_grouped_when_task_provenance_exists(self):
        with server.db() as c:
            pid = c.execute("insert into health_courses(kind,product,scope_type,start_date,dose_count,interval_days,cost_per_application,created_at) values('Aşı','Eski Şap','multi','2026-10-24',2,21,100,'2026-10-24')").lastrowid
            targets = [(int(ref.split(':')[1]), None, ref) for ref in self.refs[:2]]
            server.create_health_course_tasks(c, pid, targets, 'Aşı', '2026-10-24', 100, '', dose_count=2, interval_days=21)
        self.complete(pid)
        self.assertEqual(sorted(len(r['members']) for r in self.model()['selected']), [2, 67])

    def test_case_cost_shares_and_other_health_programs_group_by_their_provenance(self):
        for category in ('parasite', 'vitamin', 'treatment'):
            pid = self.save(self.refs[:2], category, category, '12.35')
            self.complete(pid)
        with server.db() as c:
            hc.save_case(vars(server), c, {'diagnosis': 'Muayene', 'illness_date': '2026-10-24',
                         'subjects_json': json.dumps(self.refs[:3]), 'request_key': secrets.token_urlsafe(24),
                         'veterinarian': '', 'vet_cost': '100', 'medicine_cost': '0'}, 'admin')
        model = self.model()
        self.assertEqual(sorted(len(r['members']) for r in model['selected']), [2, 2, 2, 3, 67])
        case = next(r for r in model['selected'] if r['_health']['case_id'])
        self.assertEqual(fg.cents(case['amount']), 10000)

    def test_ambiguous_health_links_are_not_grouped_or_double_counted(self):
        with server.db() as c:
            c.execute('''insert into health(animal_id,kind,product,applied_date,cost,finance_id,course_id,task_id)
                select animal_id,kind,product,applied_date,cost,finance_id,course_id,null
                from health order by id limit 1''')
        model = self.model()
        self.assertEqual(sorted(len(r['members']) for r in model['selected']), [1, 66])
        self.assertEqual(sum(fg.cents(r['amount']) for r in model['selected']), 670000)

    def test_detail_includes_all_members_and_safe_edit_links_with_escaped_text(self):
        with server.db() as c:
            c.execute("update animals set nickname='<img src=x onerror=alert(1)>' where id=?", (int(self.refs[0].split(':')[1]),))
        model = self.model()
        body, back = fg.detail(vars(server), fg.detail_url(model['selected'][0], model['filters']))
        self.assertEqual(body.count('data-finance-member data-search='), 67)
        self.assertIn('₺6.700,00', body)
        self.assertIn('/health?record_edit=', body)
        self.assertIn('&lt;img', body)
        self.assertNotIn('<img src=x', body)
        self.assertTrue(back.startswith('/finance?'))
        for raw in ('https://evil.example/finance', '//evil.example/finance', '/health', ''):
            self.assertEqual(fg.safe_return(raw), '/finance')
        self.assertIsNone(fg.detail(vars(server), '/finance/health-group?group=bad')[0])

    def test_feed_invoice_preview_and_ordinary_edit_delete_actions_are_preserved(self):
        with server.db() as c:
            fid = c.execute("insert into finance(tx_date,tx_type,category,amount,description,payment_method,due_date,payment_status,created_at,supplier,invoice_no) values('2026-10-24','Gider','Yem',250,'Yem faturası','Vadeli','2026-11-01','Bekliyor','2026-10-24','Bayi','F123')").lastrowid
            feed = c.execute("select id from feed_catalog order by id limit 1").fetchone()[0]
            c.execute('''insert into finance_feed_items(finance_id,feed_id,quantity,unit,package_kg,
                quantity_kg,unit_price,purchase_unit_price,line_total,created_at)
                values(?,?,1,'torba',50,50,5,250,250,'2026-10-24')''', (fid, feed))
        model = self.model()
        normal = next(r for r in model['visible'] if r['id'] == fid)
        row = fg.transaction_row(vars(server), normal, model)
        for marker in ('openFeedInvoicePreview', 'feedInvoicePreview'+str(fid), '/finance/mark-paid',
                       '/finance/delete', '/finance/edit?id='+str(fid), 'Bayi', 'F123'):
            self.assertIn(marker, row)

    def test_http_group_details_auth_and_concurrent_filters(self):
        http = server.QuietThreadingHTTPServer(('127.0.0.1', 0), server.App)
        threading.Thread(target=http.serve_forever, daemon=True).start()
        server.SESSIONS['finance-group-test'] = {'username': 'admin', 'role': 'admin'}
        base = 'http://127.0.0.1:' + str(http.server_port)
        def get(path, login=True):
            req = urllib.request.Request(base + path, headers={'Cookie': 'sid=finance-group-test'} if login else {})
            with urllib.request.urlopen(req, timeout=20) as response:
                return response.read().decode(), response.url
        try:
            with patch.object(server, 'license_status', return_value=(True, {}, '')):
                text, _ = get(self.url)
                self.assertEqual(text.count('data-finance-group='), 1)
                self.assertIn('1 işlem · 67 kayıt', text)
                self.assertIn('₺6.700,00', text)
                model = self.model()
                url = fg.detail_url(model['selected'][0], model['filters'])
                detail, _ = get(url)
                self.assertEqual(detail.count('data-finance-member data-search='), 67)
                _, logged_out = get(url, login=False)
                self.assertIn('/login', logged_out)
                paths = [self.url+'&category=A%C5%9F%C4%B1', self.url+'&category=Yem', self.url+'&type=Gelir'] * 3
                with ThreadPoolExecutor(max_workers=3) as pool:
                    pages = list(pool.map(get, paths))
                for path, (body, _) in zip(paths, pages):
                    self.assertEqual('data-finance-group=' in body, 'category=A' in path)
        finally:
            http.shutdown()
            http.server_close()
            server.SESSIONS.pop('finance-group-test', None)


if __name__ == '__main__':
    unittest.main()
