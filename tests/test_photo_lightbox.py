import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'app'))
import server


class PhotoLightboxTests(unittest.TestCase):
    def test_lightbox_is_injected_only_when_zoomable_photo_exists(self):
        body = '<img src="/uploads/test.webp" alt="TR123 fotoğrafı" data-photo-zoom>'
        html = server.page('Hayvan Kartı', body, '/animals', 'admin')
        self.assertIn('id="hotfix122ax-photo-lightbox"', html)
        self.assertIn('id="hotfix122ax-photo-lightbox-script"', html)
        self.assertIn("event.key==='Escape'", html)
        self.assertIn("event.target===box", html)
        self.assertIn("photo.tabIndex=0", html)
        self.assertLess(html.index('hotfix122ax-photo-lightbox'), html.index('</head>'))
        plain = server.page('Dashboard', '<p>Fotoğraf yok</p>', '/', 'admin')
        self.assertNotIn('hotfix122ax-photo-lightbox', plain)

    def test_animal_and_calf_profile_markup_is_zoomable(self):
        source = pathlib.Path(server.__file__).read_text(encoding='utf-8')
        self.assertGreaterEqual(source.count('data-photo-zoom'), 4)
        self.assertIn('data-photo-caption=', source)


if __name__ == '__main__':
    unittest.main()
