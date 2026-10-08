import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SERVER=(ROOT/"app"/"server.py").read_text(encoding="utf-8")

class Hotfix122BPTests(unittest.TestCase):
    def test_version_and_css_hook(self):
        self.assertIn("APP_VERSION='3.9.23 DEV4 Hotfix1.22bs'", SERVER)
        self.assertIn('id="hotfix122bp-reproduction-card-ui"', SERVER)
    def test_mobile_actions_are_bottom_grid(self):
        self.assertIn('grid-template-areas:\n      "identity"\n      "meta"\n      "smart"\n      "action"', SERVER)
        self.assertIn('grid-template-columns:repeat(2,minmax(0,1fr))!important', SERVER)
    def test_desktop_has_dedicated_action_column(self):
        self.assertIn('"identity meta action"', SERVER)
        self.assertIn('"identity smart action"', SERVER)
    def test_existing_smart_reproduction_kept(self):
        self.assertIn('def smart_reproduction_state(', SERVER)
        self.assertIn("life.get('code')=='dry_due'", SERVER)

if __name__=='__main__':
    unittest.main()
