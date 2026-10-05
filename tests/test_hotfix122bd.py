import sys
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'app'))
import server

class Hotfix122BDTests(unittest.TestCase):
    def test_dashboard_finance_task_links_directly_to_finance_edit(self):
        src=(ROOT/'app'/'server.py').read_text(encoding='utf-8')
        self.assertIn("'source':'finance','finance_id':int(r['id'])",src)
        self.assertIn('/finance/edit?id=',src)
        self.assertEqual(server.APP_VERSION,'3.9.23 DEV4 Hotfix1.22bh')

if __name__=='__main__':
    unittest.main()
