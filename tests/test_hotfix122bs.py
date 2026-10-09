import os, sqlite3, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app'))
import server

class Hotfix122BsTests(unittest.TestCase):
    def test_runtime_db_is_standard_connection(self):
        with tempfile.TemporaryDirectory() as td, patch.object(server, 'DB', Path(td)/'runtime.db'):
            with patch.dict(os.environ, {}, clear=False):
                os.environ.pop('CIFTLIKPRO_TEST_AUTOCLOSE_DB', None)
                con=server.db()
                self.assertIs(type(con), sqlite3.Connection)
                con.execute('create table x(id integer)')
                con.close()

    def test_test_mode_context_closes_connection(self):
        with tempfile.TemporaryDirectory() as td, patch.object(server, 'DB', Path(td)/'ci.db'), patch.dict(os.environ, {'CIFTLIKPRO_TEST_AUTOCLOSE_DB':'1'}):
            con=server.db()
            with con as c:
                c.execute('create table x(id integer)')
            with self.assertRaises(sqlite3.ProgrammingError):
                con.execute('select 1')

    def test_version(self):
        self.assertEqual(server.APP_VERSION, '3.9.23 DEV4 Hotfix1.22bz')
