"""Live-data, SQL and isolation checks for Dashboard read reuse."""
import concurrent.futures
import tempfile
import threading
import unittest
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

from test_reports_import import server
from dashboard_performance import INDEXES, request_reads


class DashboardPerformanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(server, 'DB', Path(self.temp.name)/'dashboard.db')
        self.db_patch.start()
        server.init_db()
        with server.db() as c:
            self.animal = c.execute("insert into animals(tag,gender,status) values('PERF-MOTHER','Dişi','Aktif')").lastrowid
            c.execute('insert into inseminations(animal_id,attempt,insemination_date,pregnancy_result,due_date) values(?,?,?,?,?)',
                      (self.animal,1,(server.date.today()-timedelta(days=200)).isoformat(),'Pozitif',(server.date.today()+timedelta(days=80)).isoformat()))

    def tearDown(self):
        self.db_patch.stop()
        self.temp.cleanup()

    def birth(self):
        with server.db() as c:
            c.execute('insert into calves(tag,mother_id,birth_date,gender,status) values(?,?,?,?,?)',
                      ('PERF-CALF',self.animal,server.date.today().isoformat(),'Dişi','Aktif'))

    def test_indexes_use_existing_tables_and_are_idempotent(self):
        server.init_db()
        with server.db() as c:
            names={r['name'] for r in c.execute("select name from sqlite_master where type='index'")}
            for statement in INDEXES:
                self.assertIn(statement.split()[5],names)
            plan=c.execute('explain query plan select weight from weights where animal_id=? order by measure_date desc,id desc limit 1',(self.animal,)).fetchall()
            self.assertTrue(any('idx_dash_weights_latest' in r['detail'] for r in plan))
            self.assertEqual(c.execute('select count(*) from animals').fetchone()[0],1)

    def test_repeated_dashboard_reads_match_original_with_no_repeat_sql(self):
        with server.db() as c:
            expected=server.active_pregnancy_records.__wrapped__(c)
            with request_reads():
                server.dashboard_herd_counts(c)
                actual=server.active_pregnancy_records(c)
                statements=[]
                c.set_trace_callback(statements.append)
                again=server.active_pregnancy_records(c)
                c.set_trace_callback(None)
            self.assertEqual({k:dict(v) for k,v in actual.items()},{k:dict(v) for k,v in expected.items()})
            self.assertEqual({k:dict(v) for k,v in again.items()},{k:dict(v) for k,v in expected.items()})
            self.assertEqual(statements,[])

    def test_next_request_immediately_sees_birth_and_updated_counts(self):
        with server.db() as c, request_reads():
            self.assertEqual(server.dashboard_herd_counts(c)['calf'],0)
            self.assertIn(self.animal,server.active_pregnancy_records(c))
        self.birth()
        with server.db() as c, request_reads():
            self.assertEqual(server.dashboard_herd_counts(c)['calf'],1)
            self.assertNotIn(self.animal,server.active_pregnancy_records(c))

    def test_maintenance_reads_are_fresh_before_dashboard_counts(self):
        with server.db() as c, request_reads():
            self.assertIsNotNone(server.current_pregnancy_record(c,self.animal))
            c.execute("update inseminations set pregnancy_result='Negatif' where animal_id=?",(self.animal,))
            self.assertIsNone(server.current_pregnancy_record(c,self.animal))

    def test_failed_request_does_not_reuse_reads_outside_request(self):
        with self.assertRaisesRegex(RuntimeError,'request aborted'):
            with server.db() as c, request_reads():
                server.dashboard_herd_counts(c)
                self.assertIn(self.animal,server.active_pregnancy_records(c))
                raise RuntimeError('request aborted')
        self.birth()
        with server.db() as c:
            self.assertNotIn(self.animal,server.active_pregnancy_records(c))

    def test_concurrent_request_uses_its_own_current_data(self):
        ready=threading.Event()
        updated=threading.Event()
        def first_request():
            c=server.db()
            try:
                with request_reads():
                    server.dashboard_herd_counts(c)
                    before=self.animal in server.active_pregnancy_records(c)
                    ready.set()
                    self.assertTrue(updated.wait(10))
                    after=self.animal in server.active_pregnancy_records(c)
                    return before,after
            finally:c.close()
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            pending=executor.submit(first_request)
            self.assertTrue(ready.wait(10))
            try:
                self.birth()
                with server.db() as c, request_reads():
                    server.dashboard_herd_counts(c)
                    self.assertNotIn(self.animal,server.active_pregnancy_records(c))
            finally:updated.set()
            self.assertEqual(pending.result(timeout=10),(True,True))


if __name__ == '__main__':
    unittest.main()
