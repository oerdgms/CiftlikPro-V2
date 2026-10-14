import unittest
from pathlib import Path

class MobileApi9Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s=(Path(__file__).parents[1]/'app'/'server.py').read_text(encoding='utf-8')
    def test_build_marker(self):
        self.assertIn("MOBILE_API_BUILD='MobileAPI9-FastFieldActions'",self.s)
    def test_pregnant_repro_guard_ui(self):
        self.assertIn("Gebelik sonucu / düzelt",self.s)
        self.assertIn("a.pregnant?'✓ Gebelik Sonucu / Düzenle'",self.s)
    def test_compact_actions(self):
        self.assertIn('.quick-actions',self.s)
        self.assertIn('＋ Sağlık',self.s)
    def test_backend_pregnancy_guard_preserved(self):
        self.assertIn("if is_currently_pregnant(c,aid)",self.s)
    def test_scroll_fix_preserved(self):
        self.assertIn('function topSoon()',self.s)
