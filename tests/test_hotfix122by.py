import pathlib, unittest, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'app'))
import server
SRC=(ROOT/'app'/'server.py').read_text(encoding='utf-8')
class Hotfix122BYTests(unittest.TestCase):
    def test_version(self): self.assertEqual(server.APP_VERSION,'3.9.23 DEV4 Hotfix1.22ca')
    def test_debounce_standard(self): self.assertIn('const DEBOUNCE=280',SRC)
    def test_herd_no_reload_live_search(self):
        block=SRC.split('function initHerd(){',1)[1].split('function initFeeds(){',1)[0]
        self.assertIn("fetch(url",block); self.assertIn("e.preventDefault()",block)
        self.assertNotIn('requestSubmit',block)
    def test_feed_no_reload_live_search(self):
        block=SRC.split('function initFeeds(){',1)[1].split('function debounceExisting',1)[0]
        self.assertIn("fetch(url",block); self.assertIn("e.preventDefault()",block)
    def test_focus_preserved(self): self.assertIn('focus({preventScroll:true})',SRC)
if __name__=='__main__': unittest.main()
