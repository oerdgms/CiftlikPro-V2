import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'app'))
import server


class Hotfix122BFTests(unittest.TestCase):
    def test_desktop_dashboard_uses_balanced_three_column_flow(self):
        html=server.page('Dashboard','<section class="v117-dashboard"></section>','/','admin')
        self.assertIn('.v117-dashboard>.v117-panel:nth-child(1){grid-row:span 2}',html)
        self.assertIn('.v117-dashboard>.v117-panel:nth-child(4){grid-column:2}',html)
        self.assertIn('.v117-dashboard>.v117-panel:nth-child(5){grid-column:3}',html)
        self.assertNotIn('body.v118-shell .v117-dashboard>.v122au-task-panel{grid-row:auto',html)

    def test_release_version_is_122bf(self):
        self.assertEqual(server.APP_VERSION,'3.9.23 DEV4 Hotfix1.22bh')
        self.assertEqual(server.APP_LABEL,'v3.9.23 DEV4 Hotfix1.22bh')


if __name__=='__main__':
    unittest.main()
