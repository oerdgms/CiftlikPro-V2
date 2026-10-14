from pathlib import Path
import py_compile, unittest
class V8(unittest.TestCase):
 def setUp(self): self.p=Path(__file__).parents[1]/'app'/'server.py'; self.s=self.p.read_text(encoding='utf-8')
 def test_compile(self): py_compile.compile(str(self.p),doraise=True)
 def test_identity(self): self.assertIn("MOBILE_API_BUILD='MobileFullV13-EnterpriseParity-SharedLogic'",self.s)
 def test_finance_fix(self):
  self.assertIn("'/api/v1/finance/save'",self.s); self.assertIn('cache.financeCategories=j.categories',self.s); self.assertIn('normalize_finance_type(cat,typ)',self.s)
 def test_health_plan(self):
  self.assertIn("path=='/api/v1/health/plan'",self.s); self.assertIn('＋ Plan Oluştur',self.s); self.assertIn('＋ Sağlık Kaydı',self.s)
if __name__=='__main__': unittest.main()
