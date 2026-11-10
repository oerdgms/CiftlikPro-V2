import io
import json
import unittest
from pathlib import Path
from PIL import Image

import test_app_edition as app_tests
import release_info as release

ROOT = Path(__file__).resolve().parents[1]


class PWAHTTPTests(unittest.TestCase):
    setUp = app_tests.AppEditionTests.setUp
    tearDown = app_tests.AppEditionTests.tearDown
    get = app_tests.AppEditionTests.get

    def test_public_manifest_has_distinct_maskable_icon_and_same_origin_shortcuts(self):
        status, headers, body, _ = self.get('/app-manifest.json', False)
        self.assertEqual(status, 200)
        self.assertEqual(headers['Content-Type'], 'application/manifest+json')
        self.assertNotIn('immutable', headers['Cache-Control'])
        manifest = json.loads(body)
        self.assertEqual(manifest['id'], '/')
        self.assertEqual(manifest['scope'], '/')
        self.assertEqual(manifest['start_url'], '/')
        self.assertEqual(manifest['display'], 'standalone')
        self.assertEqual({icon['purpose'] for icon in manifest['icons']}, {'any', 'maskable'})
        for icon in manifest['icons']:
            image = Image.open(io.BytesIO(self.get(icon['src'], False)[2]))
            self.assertEqual(icon['sizes'], f'{image.width}x{image.height}')
            if icon['purpose'] == 'maskable':
                self.assertEqual(image.convert('RGB').getpixel((0, 0)), (6, 62, 43))
        self.assertEqual([item['url'] for item in manifest['shortcuts']], ['/all-animals', '/modules'])

    def test_apple_icon_and_install_controller_are_linked_on_login_and_live_pages(self):
        for route in ('/login', '/modules', '/all-animals', '/ration-workbench?id=1'):
            html = self.get(route, route != '/login')[2].decode()
            self.assertEqual(html.count('src="/app-assets/pwa.js?v='+release.VERSION+'"'), 1)
            self.assertIn('href="/app-assets/pwa.css?v='+release.VERSION+'"', html)
            self.assertIn('rel="apple-touch-icon" href="/app-assets/apple-touch-icon.png"', html)
            self.assertEqual(html.count('rel="manifest"'), 1)
        image = Image.open(io.BytesIO(self.get('/app-assets/apple-touch-icon.png', False)[2]))
        self.assertEqual(image.size, (180, 180))

    def test_new_assets_are_public_and_versioned_but_worker_revalidates(self):
        for name in ('pwa.js', 'pwa.css', 'apple-touch-icon.png', 'icon-maskable-512.png'):
            status, headers, body, _ = self.get('/app-assets/'+name+'?v='+release.VERSION, False)
            self.assertEqual(status, 200)
            self.assertGreater(len(body), 100)
            self.assertIn('immutable', headers['Cache-Control'])
        _, headers, _, _ = self.get('/app-service-worker.js', False)
        self.assertEqual(headers['Service-Worker-Allowed'], '/')
        self.assertNotIn('immutable', headers['Cache-Control'])
