import unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'app'))
import server

class Hotfix122BWTests(unittest.TestCase):
    def test_version(self):
        self.assertEqual(server.APP_VERSION,'3.9.23 DEV4 Hotfix1.22ca')
    def test_toolbar_css_hides_camera_file_input(self):
        css=server.HOTFIX122BW_HERD
        self.assertIn('input[type="file"][hidden]',css)
        self.assertIn('display:none!important',css)
    def test_toolbar_uses_real_grid_not_display_contents(self):
        css=server.HOTFIX122BW_HERD
        self.assertIn('.hf122bt-herd-search-row{',css)
        self.assertIn('display:grid!important',css)
        self.assertIn('grid-template-columns:minmax(0,1fr) 74px 44px',css)
    def test_installer_and_workflow_version(self):
        wf=(ROOT/'.github/workflows/windows-installer.yml').read_text(encoding='utf-8')
        iss=(ROOT/'installer.iss').read_text(encoding='utf-8')
        self.assertIn('Hotfix1.22ca',wf)
        self.assertIn('Hotfix1_22ca',wf)
        self.assertIn('Hotfix1.22ca',iss)
        self.assertIn('Hotfix1_22ca',iss)

if __name__=='__main__': unittest.main()
