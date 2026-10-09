import pathlib, unittest, sys
sys.path.insert(0, str(pathlib.Path('app').resolve()))
import server

class Hotfix122BZTests(unittest.TestCase):
    def test_version(self):
        self.assertEqual(server.APP_VERSION, '3.9.23 DEV4 Hotfix1.22cd')
    def test_archive_mobile_card_css(self):
        src=pathlib.Path('app/server.py').read_text(encoding='utf-8')
        self.assertIn('.archive-tabs', src)
        self.assertIn('.archive-loss-table', src)
        self.assertIn('.archive-card-head', src)
        self.assertIn("tr class=\"data-row\"", src)
    def test_archive_tabs_all_categories(self):
        src=pathlib.Path('app/server.py').read_text(encoding='utf-8')
        for target in ('/all-animals','/archive/sold','/archive/slaughtered','/archive/lost'):
            self.assertIn(target, src)
    def test_archive_photos_and_status(self):
        src=pathlib.Path('app/server.py').read_text(encoding='utf-8')
        self.assertIn('archive-thumb', src)
        self.assertIn('archive-status-sold', src)
        self.assertIn('archive-status-cut', src)
        self.assertIn('archive-status-lost', src)

if __name__=='__main__': unittest.main()
