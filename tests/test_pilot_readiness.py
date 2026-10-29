import json
import re
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import test_app_edition as app_tests
import mobile_ui
import release_info as release

ROOT = Path(__file__).resolve().parents[1]


class ReleaseIdentityTests(unittest.TestCase):
    def test_distribution_metadata_matches_runtime(self):
        self.assertEqual(json.loads((ROOT/'RELEASE.json').read_text()),release.metadata())
        self.assertEqual(mobile_ui.BUILD,release.BUILD)
        self.assertEqual(app_tests.server.APP_VERSION,release.CORE_VERSION)
        self.assertIn("const CACHE = '"+release.CACHE_NAME+"';",(ROOT/'app/mobile_assets/service-worker.js').read_text())
        self.assertIn('OutputBaseFilename='+release.SETUP_STEM,(ROOT/'installer.iss').read_text())
        self.assertIn(release.SETUP_FILE,(ROOT/'.github/workflows/windows-installer.yml').read_text())
        self.assertIn('"release_info"',(ROOT/'CiftlikPro.spec').read_text())

    def test_release_check_is_read_only_and_passes(self):
        tracked=[ROOT/'RELEASE.json',ROOT/'installer.iss',ROOT/'.github/workflows/windows-installer.yml',ROOT/'app/mobile_assets/service-worker.js']
        before=[p.read_bytes() for p in tracked]
        result=subprocess.run([sys.executable,str(ROOT/'scripts/sync_release.py'),'--check'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertEqual(before,[p.read_bytes() for p in tracked])

    def test_asset_rewrite_tracks_next_version_without_changing_forms(self):
        original='<script src="/app-assets/shared.js?v=2.0.29"></script><link href="/app-assets/reproduction.css"><form action="/animal-edit?id=8"><input name="notes" value="keep"></form>'
        with patch.object(release,'VERSION','9.8.7'):
            result=release.version_assets(original)
            self.assertIn('shared.js?v=9.8.7',result)
            self.assertIn('reproduction.css?v=9.8.7',result)
            self.assertEqual(result,release.version_assets(result))
        self.assertIn('<form action="/animal-edit?id=8"><input name="notes" value="keep"></form>',result)

    def test_service_worker_never_caches_business_records(self):
        source=(ROOT/'app/mobile_assets/service-worker.js').read_text()
        self.assertIn("event.request.method !== 'GET'",source)
        self.assertIn("fetch(event.request).catch",source)
        self.assertNotIn('cache.put(',source)
        self.assertIn("updateViaCache:'none'",(ROOT/'app/mobile_assets/mobile.js').read_text())

    def test_offline_retry_has_timeout_and_preserves_requested_page(self):
        source=(ROOT/'app/mobile_assets/offline.html').read_text()
        self.assertIn("fetch('/app-build.json'",source)
        self.assertIn('controller.abort(),6000',source)
        self.assertIn('location.reload()',source)
        self.assertNotIn('/mobile-api/ping',source)
        self.assertNotIn("location.href='/mobile'",source)


class ReleaseHTTPTests(unittest.TestCase):
    setUp=app_tests.AppEditionTests.setUp
    tearDown=app_tests.AppEditionTests.tearDown
    get=app_tests.AppEditionTests.get

    def test_build_probe_is_public_non_sensitive_and_not_cached(self):
        status,headers,data,_=self.get('/app-build.json',False)
        self.assertEqual(status,200)
        self.assertEqual(headers['Cache-Control'],'no-store')
        metadata=json.loads(data)
        self.assertEqual(metadata,release.metadata())
        for field in ('users','password','license_key','session','db_path'):
            self.assertNotIn(field,metadata)

    def test_old_asset_keys_and_worker_are_not_immutable(self):
        for path in ('/app-assets/mobile.css?v=2.0.41','/app-assets/mobile.css?v=invalid','/app-service-worker.js?v='+release.VERSION):
            self.assertNotIn('immutable',self.get(path,False)[1]['Cache-Control'])
        headers=self.get('/app-assets/mobile.css?v='+release.VERSION,False)[1]
        self.assertIn('immutable',headers['Cache-Control'])
        self.assertEqual(headers['Vary'],'Accept-Encoding')

    def test_live_pages_use_one_asset_version(self):
        for route in ('/login','/farm-profile','/all-animals','/health','/milk-center','/rations'):
            text=self.get(route)[2].decode()
            versions=re.findall(r'/app-assets/[\w.-]+\.(?:css|js|jpg)\?v=([\w.-]+)',text)
            self.assertTrue(versions,route)
            self.assertEqual(set(versions),{release.VERSION},route)

    def test_nested_css_image_uses_current_version(self):
        css=self.get('/app-assets/mobile.css?v='+release.VERSION,False)[2].decode()
        self.assertIn('/app-assets/login.jpg?v='+release.VERSION,css)
        self.assertNotIn('/app-assets/login.jpg?v=2.0.10',css)
