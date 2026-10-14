from pathlib import Path
import py_compile, unittest
class MobileFullV10(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=Path(__file__).parents[1]/'app'/'server.py'
        cls.s=cls.p.read_text(encoding='utf-8')
    def test_compile(self): py_compile.compile(str(self.p),doraise=True)
    def test_identity(self): self.assertIn("MOBILE_API_BUILD='MobileFullV13-EnterpriseParity-SharedLogic'",self.s)
    def test_no_finance_total_badge(self): self.assertNotIn('<h2>₺ Finans</h2><span class="pill">${j.count} kayıt</span>',self.s)
    def test_app_overflow_lock(self):
        self.assertIn('overscroll-behavior-x:none',self.s); self.assertIn('touch-action:pan-y',self.s)
    def test_health_actions(self):
        self.assertIn('＋ Sağlık Kaydı',self.s); self.assertIn('＋ Plan Oluştur',self.s); self.assertIn("api('/health/plan'",self.s)
    def test_field_modules(self):
        for marker in ('filterMobileFeeds','filterMobileRations','saveRation','savePaddockMove','reproductionCenter'):
            self.assertIn(marker,self.s)
    def test_finance_backend_kept(self): self.assertIn("'/api/v1/finance/save'",self.s)
if __name__=='__main__': unittest.main()
