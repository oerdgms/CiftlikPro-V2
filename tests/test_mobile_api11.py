import unittest
from pathlib import Path
S=Path(__file__).parents[1].joinpath('app/server.py').read_text(encoding='utf-8')
class MobileApi11Tests(unittest.TestCase):
 def test_build(self): self.assertIn("MOBILE_API_BUILD='MobileFullV13-EnterpriseParity-SharedLogic'",S)
 def test_weight_api(self):
  self.assertIn("if path=='/api/v1/weight':",S);self.assertIn("insert into weights",S)
 def test_photo_api(self):
  self.assertIn("if path=='/api/v1/photo':",S);self.assertIn('optimized_webp_bytes(content)',S)
 def test_animal_detail_parity(self):
  self.assertIn("data['weights']",S);self.assertIn("data['finance_summary']",S);self.assertIn("data['photos']",S)
 def test_mobile_ui(self):
  self.assertIn('weightForm(',S);self.assertIn('photoForm(',S);self.assertIn("data['finance_summary']",S)
 def test_existing_parity_preserved(self):
  self.assertIn('paddock_population',S);self.assertIn("if path=='/api/v1/tasks/complete':",S)
if __name__=='__main__':unittest.main()
