from pathlib import Path
import unittest
S=Path(__file__).parents[1].joinpath('app/server.py').read_text(encoding='utf-8')
class MobileFullV12(unittest.TestCase):
 def test_identity(self): self.assertIn("MOBILE_API_BUILD='MobileFullV13-EnterpriseParity-SharedLogic'",S); self.assertIn("APP_VERSION='3.9.23 DEV4 Hotfix1.22cr'",S)
 def test_center_nav(self):
  self.assertIn('Ana Sayfa</button><button data-v="animals"',S); self.assertIn('id="globalFab" class="fab"',S); self.assertNotIn('data-v="paddocks" onclick="show(\'paddocks\')"><span class="ico">▦</span>Padoklar</button>',S)
 def test_feed_filters(self): self.assertIn('data-stock="${Number(r.stock||0)}"',S); self.assertIn("mode==='stock'&&(state==='available'||state==='low')",S); self.assertIn("mode==='low'&&state==='low'",S)
 def test_health_repeat(self): self.assertIn('X gün arayla / X doz',S); self.assertIn("dose_count:Number(el('haDose').value||2)",S); self.assertIn("interval_days:Number(el('haInterval').value||15)",S)
 def test_horizontal_lock(self): self.assertIn('overflow-x:hidden;overscroll-behavior-x:none',S)
if __name__=='__main__': unittest.main()
