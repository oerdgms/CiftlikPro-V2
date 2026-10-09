import unittest
from pathlib import Path

SERVER=(Path(__file__).resolve().parents[1]/"app"/"server.py").read_text(encoding="utf-8")

class Hotfix122BRTests(unittest.TestCase):
    def test_reproduction_updates_bypass_general_record_dedupe(self):
        self.assertIn("dedupe_exempt_paths={'/reproduction-status','/reproduction/dry','/reproduction/dry-cancel'}",SERVER)

    def test_runtime_db_uses_standard_sqlite_connection(self):
        self.assertIn("os.environ.get('CIFTLIKPRO_TEST_AUTOCLOSE_DB') == '1'",SERVER)
        self.assertIn('factory = _TestAutoClosingConnection',SERVER)
        self.assertIn('else sqlite3.Connection',SERVER)
        self.assertNotIn('class AutoClosingConnection(sqlite3.Connection):',SERVER)

    def test_current_version(self):
        self.assertIn("APP_VERSION='3.9.23 DEV4 Hotfix1.22cd'",SERVER)

if __name__=='__main__': unittest.main()
