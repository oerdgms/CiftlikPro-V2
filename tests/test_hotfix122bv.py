import unittest
from pathlib import Path

from test_reports_import import server


class Hotfix122BVTests(unittest.TestCase):
    def test_search_camera_row_uses_single_responsive_grid(self):
        source=Path(server.__file__).read_text(encoding='utf-8')
        self.assertIn('body.hf122am-herd label.herd-search{',source)
        self.assertIn('grid-template-rows:auto 44px!important',source)
        self.assertIn('display:contents!important',source)
        self.assertIn("grid-template-columns:minmax(0,1fr) 74px 44px!important",source)
        self.assertIn("grid-template-columns:minmax(0,1fr) 66px 44px!important",source)
        self.assertIn("file.setAttribute('capture','environment')",source)

    def test_version(self):
        self.assertEqual(server.APP_VERSION,'3.9.23 DEV4 Hotfix1.22ca')
        self.assertEqual(server.APP_LABEL,'v3.9.23 DEV4 Hotfix1.22ca')


if __name__=='__main__':
    unittest.main()
