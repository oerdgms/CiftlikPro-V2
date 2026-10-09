import pathlib, sys, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]/"app"))
import server

class Hotfix122BXTests(unittest.TestCase):
    def test_version(self):
        self.assertEqual(server.APP_VERSION, "3.9.23 DEV4 Hotfix1.22ca")
    def test_new_filterbar_markup_and_css(self):
        src=pathlib.Path(server.__file__).read_text(encoding="utf-8")
        self.assertIn("herd-filter-bx-row", src)
        self.assertIn("hotfix122bx-herd-filterbar", src)
        self.assertIn("grid-template-columns:minmax(340px,1.35fr) minmax(500px,1.65fr)", src)
        self.assertIn("herd-category-strip", src)
    def test_page_injects_bx_css(self):
        html=server.page("Tüm Aktif Hayvanlar","<div></div>","/all-animals","admin")
        self.assertIn("hotfix122bx-herd-filterbar", html)
        self.assertNotIn('type="file" name="code_image"', html)

if __name__=="__main__": unittest.main()
