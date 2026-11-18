"""Run every regression with timings and disposable SQLite I/O tuning.

This script is never imported by the application or the Windows executable.
Transactions, constraints and rollback remain enabled. Only synchronous disk
flushes on databases under the OS temporary directory are disabled; tests do
not model power-loss durability. --durable-db keeps normal SQLite flushing.
"""
import argparse
import faulthandler
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]


def disposable_database(database):
    try:
        name = os.fsdecode(os.fspath(database))
        if name == ':memory:' or name.startswith('file:'):
            return False
        return Path(name).resolve().is_relative_to(Path(tempfile.gettempdir()).resolve())
    except (TypeError, ValueError, OSError):
        return False


class TimedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timings = []

    def startTest(self, test):
        self.started = time.perf_counter()
        super().startTest(test)
        self.stream.flush()
        # A hung test produces thread stacks before the CI job timeout.
        faulthandler.dump_traceback_later(120, repeat=True)

    def stopTest(self, test):
        faulthandler.cancel_dump_traceback_later()
        elapsed = time.perf_counter() - self.started
        self.timings.append({'test': test.id(), 'seconds': round(elapsed, 3)})
        self.stream.writeln(f'[TEST PERF] {elapsed:.3f}s {test.id()}')
        self.stream.flush()
        super().stopTest(test)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--durable-db', action='store_true')
    parser.add_argument('--pattern', default='test*.py')
    args = parser.parse_args()
    os.chdir(ROOT)
    os.environ['CIFTLIKPRO_TEST_AUTOCLOSE_DB'] = '1'
    os.environ['PYTHONUNBUFFERED'] = '1'
    original_connect = sqlite3.connect
    tuned = 0

    def test_connect(database, *pos, **kw):
        nonlocal tuned
        connection = original_connect(database, *pos, **kw)
        if not args.durable_db and disposable_database(database):
            try:
                connection.execute('PRAGMA synchronous=OFF')
                tuned += 1
            except Exception:
                connection.close()
                raise
        return connection

    sqlite3.connect = test_connect
    try:
        suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern=args.pattern)
        runner = unittest.TextTestRunner(verbosity=2, resultclass=TimedResult)
        result = runner.run(suite)
    finally:
        sqlite3.connect = original_connect
        faulthandler.cancel_dump_traceback_later()
    timings = sorted(result.timings, key=lambda row: row['seconds'], reverse=True)
    report = {'tests': result.testsRun, 'successful': result.wasSuccessful(),
              'failures': len(result.failures), 'errors': len(result.errors),
              'skipped': len(result.skipped), 'temporary_connections_tuned': tuned,
              'durable_db': args.durable_db, 'timings': timings}
    (ROOT / 'test-timings.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print('\nSlowest 20 tests:', flush=True)
    for row in timings[:20]:
        print(f"{row['seconds']:8.3f}s {row['test']}", flush=True)
    print(f'Temporary SQLite connections tuned: {tuned}', flush=True)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
