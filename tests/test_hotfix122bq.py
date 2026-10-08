import sqlite3
import unittest
from pathlib import Path

SERVER=(Path(__file__).resolve().parents[1]/"app"/"server.py").read_text(encoding="utf-8")

class Hotfix122BQTests(unittest.TestCase):
    def test_reproduction_updates_bypass_general_record_dedupe(self):
        self.assertIn("dedupe_exempt_paths={'/reproduction-status','/reproduction/dry','/reproduction/dry-cancel'}",SERVER)

    def test_db_context_manager_closes_connection(self):
        self.assertIn('class AutoClosingConnection(sqlite3.Connection):',SERVER)
        self.assertIn('finally:\n            self.close()',SERVER)

    def test_current_version(self):
        self.assertIn("APP_VERSION='3.9.23 DEV4 Hotfix1.22bq'",SERVER)

if __name__=='__main__': unittest.main()
