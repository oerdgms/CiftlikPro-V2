import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'app'))
import server


class MobileAnimalActionsTests(unittest.TestCase):
    def test_compact_action_row_is_scoped_and_loaded_in_head(self):
        html = server.page('Test', '<main>İçerik</main>', '/all-animals', 'admin')
        marker = 'hotfix122al-mobile-animal-actions'
        self.assertEqual(server.APP_VERSION, '3.9.23 DEV4 Hotfix1.22ca')
        self.assertIn(marker, html)
        self.assertLess(html.index(marker), html.index('</head>'))
        self.assertIn('td[data-label="İşlemler"]', html)
        self.assertIn('grid-template-columns:minmax(0,1fr) minmax(0,1fr) 46px', html)
        self.assertIn('min-height:44px', html)
        self.assertEqual(html.count('id="hotfix122at-mobile-herd-views"'), 1)
        self.assertIn("content:'👁'!important", html)
        self.assertIn("content:'✎'!important", html)


if __name__ == '__main__':
    unittest.main()
